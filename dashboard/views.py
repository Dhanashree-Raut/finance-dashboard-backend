from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta, date
from django.db.models.functions import TruncDay, TruncMonth
from finance.models import Transaction
from users.permissions import IsAnalystOrAbove


class DashboardSummaryView(APIView):
    permission_classes = [IsAnalystOrAbove]

    def get(self, request):
        qs = Transaction.objects.filter(is_deleted=False)

        total_income   = qs.filter(type='income').aggregate(t=Sum('amount'))['t'] or 0
        total_expenses = qs.filter(type='expense').aggregate(t=Sum('amount'))['t'] or 0
        net_balance    = total_income - total_expenses

        category_totals = (
            qs.values('category', 'type')
              .annotate(total=Sum('amount'))
              .order_by('-total')
        )
        recent = qs.order_by('-date')[:5].values(
            'id', 'amount', 'type', 'category', 'date'
        )
        six_months_ago = timezone.now().date() - timedelta(days=180)
        monthly = (
            qs.filter(date__gte=six_months_ago)
              .annotate(month=TruncMonth('date'))
              .values('month', 'type')
              .annotate(total=Sum('amount'))
              .order_by('month')
        )
        return Response({
            'total_income':    total_income,
            'total_expenses':  total_expenses,
            'net_balance':     net_balance,
            'category_totals': list(category_totals),
            'recent_activity': list(recent),
            'monthly_trend':   list(monthly),
        })


class AnalyticsView(APIView):
    permission_classes = [IsAnalystOrAbove]

    def get(self, request):
        today_date = date.today()
        date_from  = request.query_params.get('date_from')
        date_to    = request.query_params.get('date_to')

        try:
            start = date.fromisoformat(date_from) if date_from else today_date - timedelta(days=30)
            end   = date.fromisoformat(date_to)   if date_to   else today_date
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)

        if start > end:
            return Response({'error': 'date_from must be before date_to.'}, status=400)

        qs = Transaction.objects.filter(
            is_deleted=False,
            date__gte=start,
            date__lte=end,
        )

        # Summary totals
        total_income   = qs.filter(type='income').aggregate(t=Sum('amount'))['t'] or 0
        total_expenses = qs.filter(type='expense').aggregate(t=Sum('amount'))['t'] or 0
        net_balance    = float(total_income) - float(total_expenses)

        # Daily income vs expense
        daily_income = (
            qs.filter(type='income')
              .annotate(day=TruncDay('date'))
              .values('day')
              .annotate(total=Sum('amount'))
              .order_by('day')
        )
        daily_expense = (
            qs.filter(type='expense')
              .annotate(day=TruncDay('date'))
              .values('day')
              .annotate(total=Sum('amount'))
              .order_by('day')
        )

        # ✅ THE FIX — no .date() call, the value is already a date object
        income_map  = {r['day']: float(r['total']) for r in daily_income}
        expense_map = {r['day']: float(r['total']) for r in daily_expense}

        all_days = sorted(set(income_map.keys()) | set(expense_map.keys()))

        line_chart = []
        running_balance = 0
        for d in all_days:
            inc = income_map.get(d, 0)
            exp = expense_map.get(d, 0)
            running_balance += inc - exp
            line_chart.append({
                'date':    d.isoformat(),   # ✅ safe — d is already a date
                'income':  inc,
                'expense': exp,
                'balance': round(running_balance, 2),
            })

        # Category breakdown
        category_totals = list(
            qs.values('category', 'type')
              .annotate(total=Sum('amount'))
              .order_by('-total')
        )
        for c in category_totals:
            c['total'] = float(c['total'])

        # Monthly trend
        monthly_income = (
            qs.filter(type='income')
              .annotate(month=TruncMonth('date'))
              .values('month')
              .annotate(total=Sum('amount'))
              .order_by('month')
        )
        monthly_expense = (
            qs.filter(type='expense')
              .annotate(month=TruncMonth('date'))
              .values('month')
              .annotate(total=Sum('amount'))
              .order_by('month')
        )

        # ✅ THE FIX — same here, no .date() call needed
        mi_map = {r['month']: float(r['total']) for r in monthly_income}
        me_map = {r['month']: float(r['total']) for r in monthly_expense}

        all_months = sorted(set(mi_map.keys()) | set(me_map.keys()))

        monthly_trend = [{
            'month':   m.strftime('%b %Y'),
            'income':  mi_map.get(m, 0),
            'expense': me_map.get(m, 0),
        } for m in all_months]

        return Response({
            'period':          {'from': start.isoformat(), 'to': end.isoformat()},
            'summary': {
                'total_income':   float(total_income),
                'total_expenses': float(total_expenses),
                'net_balance':    net_balance,
            },
            'line_chart':      line_chart,
            'category_totals': category_totals,
            'monthly_trend':   monthly_trend,
        })