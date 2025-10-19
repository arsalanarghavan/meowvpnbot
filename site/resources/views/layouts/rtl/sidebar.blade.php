<aside class="page-sidebar">
   <div class="sidebar-user text-center">
      <div>
         <img class="img-60 rounded-circle lazyloaded blur-up" src="{{asset('assets/images/dashboard/man.png')}}" alt="#">
      </div>
      <h6 class="mt-3 f-12">پنل مدیریت</h6>
   </div>
   <ul class="sidebar-menu">
      <li>
         <a class="sidebar-header {{ request()->routeIs('dashboard') ? 'active' : '' }}" href="{{ route('dashboard') }}">
            <i data-feather="home"></i><span>داشبورد</span>
         </a>
      </li>
      
      <li>
         <a class="sidebar-header {{ request()->routeIs('users.*') ? 'active' : '' }}" href="{{ route('users.index') }}">
            <i data-feather="users"></i><span>مدیریت کاربران</span>
         </a>
      </li>
      
      <li>
         <a class="sidebar-header {{ request()->routeIs('services.*') ? 'active' : '' }}" href="{{ route('services.index') }}">
            <i data-feather="server"></i><span>مدیریت سرویس‌ها</span>
         </a>
      </li>
      
      <li>
         <a class="sidebar-header {{ request()->routeIs('plans.*') ? 'active' : '' }}" href="{{ route('plans.index') }}">
            <i data-feather="package"></i><span>مدیریت پلن‌ها</span>
         </a>
      </li>
      
      <li>
         <a class="sidebar-header {{ request()->routeIs('panels.*') ? 'active' : '' }}" href="{{ route('panels.index') }}">
            <i data-feather="box"></i><span>مدیریت پنل‌ها</span>
         </a>
      </li>
      
      <li>
         <a class="sidebar-header {{ request()->routeIs('transactions.*') ? 'active' : '' }}" href="{{ route('transactions.index') }}">
            <i data-feather="dollar-sign"></i><span>تراکنش‌ها و مالی</span>
         </a>
      </li>
      
      <li>
         <a class="sidebar-header {{ request()->routeIs('marketers.*') ? 'active' : '' }}" href="{{ route('marketers.index') }}">
            <i data-feather="trending-up"></i><span>مدیریت بازاریاب‌ها</span>
         </a>
      </li>
      
      <li>
         <a class="sidebar-header {{ request()->routeIs('gift-cards.*') ? 'active' : '' }}" href="{{ route('gift-cards.index') }}">
            <i data-feather="gift"></i><span>کارت‌های هدیه</span>
         </a>
      </li>
      
      <li>
         <a class="sidebar-header {{ request()->routeIs('card-accounts.*') ? 'active' : '' }}" href="{{ route('card-accounts.index') }}">
            <i data-feather="credit-card"></i><span>کارت‌های بانکی</span>
         </a>
      </li>
      
      <li>
         <a class="sidebar-header {{ request()->routeIs('settings.*') ? 'active' : '' }}" href="{{ route('settings.index') }}">
            <i data-feather="settings"></i><span>تنظیمات</span>
         </a>
      </li>

      <li class="sidebar-header">
         <span>ابزارها</span>
      </li>

      <li>
         <a class="sidebar-header" href="#" onclick="event.preventDefault(); if(confirm('آیا مطمئن هستید؟')) location.reload();">
            <i data-feather="refresh-cw"></i><span>بروزرسانی</span>
         </a>
      </li>

      <li>
         <a class="sidebar-header" href="{{ route('clear.cache') }}" onclick="return confirm('آیا می‌خواهید کش را پاک کنید؟')">
            <i data-feather="trash-2"></i><span>پاک کردن کش</span>
         </a>
      </li>

      <li class="sidebar-header">
         <span>نمونه‌های قالب</span>
      </li>

      <li>
         <a class="sidebar-header" href="javascript:void(0)">
            <i data-feather="layers"></i><span>استارتر کیت</span><i class="fa fa-angle-right pull-left"></i>
         </a>
         <ul class="sidebar-submenu">
            <li><a href="{{ route('layout-light') }}">Layout Light</a></li>
            <li><a href="{{ route('layout-dark') }}">Layout Dark</a></li>
            <li><a href="{{ route('sidebar-fixed') }}">Sidebar Fixed</a></li>
            <li><a href="{{ route('boxed') }}">Boxed</a></li>
            <li><a href="{{ route('layout-rtl') }}">Layout RTL</a></li>
            <li><a href="{{ route('vertical') }}">Vertical</a></li>
            <li><a href="{{ route('mega-menu') }}">Mega Menu</a></li>
         </ul>
      </li>
   </ul>
</aside>
