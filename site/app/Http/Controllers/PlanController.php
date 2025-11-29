<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

class PlanController extends Controller
{
    /**
     * نمایش لیست پلن‌ها
     */
    public function index()
    {
        if (!$this->botDatabaseExists()) {
            return redirect()->back()->with('error', 'دیتابیس ربات یافت نشد!');
        }

        $pdo = $this->getBotConnection();
        
        $stmt = $pdo->prepare("SELECT * FROM plans ORDER BY category, price");
        $stmt->execute();
        $plans = $stmt->fetchAll(\PDO::FETCH_ASSOC);
        
        // آمار هر پلن
        foreach ($plans as &$plan) {
            $stmt = $pdo->prepare("
                SELECT COUNT(*) as total,
                       SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) as active
                FROM services 
                WHERE plan_id = :plan_id
            ");
            $stmt->execute(['plan_id' => $plan['id']]);
            $stats = $stmt->fetch(\PDO::FETCH_ASSOC);
            $plan['services_count'] = $stats['total'];
            $plan['active_services_count'] = $stats['active'];
        }
        
        return view('plans.index', compact('plans'));
    }

    /**
     * نمایش فرم ایجاد پلن جدید
     */
    public function create()
    {
        return view('plans.create');
    }

    /**
     * ذخیره پلن جدید
     */
    public function store(Request $request)
    {
        $request->validate([
            'name' => 'required|max:100',
            'category' => 'required|in:عادی,ویژه,گیمینگ,ترید',
            'duration_days' => 'required|integer|min:1',
            'traffic_gb' => 'required|integer|min:0',
            'price' => 'required|integer|min:0',
            'device_limit' => 'required|integer|min:1',
        ]);

        if (!$this->botDatabaseExists()) {
            return redirect()->back()->with('error', 'دیتابیس ربات یافت نشد!');
        }

        try {
            $pdo = $this->getBotConnection();
            
            $stmt = $pdo->prepare("
                INSERT INTO plans (name, category, duration_days, traffic_gb, price, device_limit, is_test_plan)
                VALUES (:name, :category, :duration_days, :traffic_gb, :price, :device_limit, 0)
            ");
            
            $stmt->execute([
                'name' => $request->name,
                'category' => $request->category,
                'duration_days' => $request->duration_days,
                'traffic_gb' => $request->traffic_gb,
                'price' => $request->price,
                'device_limit' => $request->device_limit,
            ]);
            
            return redirect()->route('plans.index')->with('success', 'پلن با موفقیت ایجاد شد!');
            
        } catch (\Exception $e) {
            return redirect()->back()->with('error', $e->getMessage());
        }
    }

    /**
     * نمایش فرم ویرایش پلن
     */
    public function edit($id)
    {
        if (!$this->botDatabaseExists()) {
            return redirect()->back()->with('error', 'دیتابیس ربات یافت نشد!');
        }

        $pdo = $this->getBotConnection();
        
        $stmt = $pdo->prepare("SELECT * FROM plans WHERE id = :id");
        $stmt->execute(['id' => $id]);
        $plan = $stmt->fetch(\PDO::FETCH_ASSOC);
        
        if (!$plan) {
            return redirect()->back()->with('error', 'پلن یافت نشد!');
        }
        
        return view('plans.edit', compact('plan'));
    }

    /**
     * ویرایش پلن
     */
    public function update(Request $request, $id)
    {
        $request->validate([
            'name' => 'required|max:100',
            'category' => 'required|in:عادی,ویژه,گیمینگ,ترید',
            'duration_days' => 'required|integer|min:1',
            'traffic_gb' => 'required|integer|min:0',
            'price' => 'required|integer|min:0',
            'device_limit' => 'required|integer|min:1',
        ]);

        if (!$this->botDatabaseExists()) {
            return redirect()->back()->with('error', 'دیتابیس ربات یافت نشد!');
        }

        try {
            $pdo = $this->getBotConnection();
            
            $stmt = $pdo->prepare("
                UPDATE plans 
                SET name = :name,
                    category = :category,
                    duration_days = :duration_days,
                    traffic_gb = :traffic_gb,
                    price = :price,
                    device_limit = :device_limit
                WHERE id = :id
            ");
            
            $stmt->execute([
                'name' => $request->name,
                'category' => $request->category,
                'duration_days' => $request->duration_days,
                'traffic_gb' => $request->traffic_gb,
                'price' => $request->price,
                'device_limit' => $request->device_limit,
                'id' => $id,
            ]);
            
            return redirect()->route('plans.index')->with('success', 'پلن با موفقیت ویرایش شد!');
            
        } catch (\Exception $e) {
            return redirect()->back()->with('error', $e->getMessage());
        }
    }

    /**
     * حذف پلن
     */
    public function destroy($id)
    {
        if (!$this->botDatabaseExists()) {
            return response()->json(['success' => false, 'message' => 'دیتابیس یافت نشد!']);
        }

        try {
            $pdo = $this->getBotConnection();
            
            // بررسی اینکه آیا سرویسی با این پلن وجود دارد
            $stmt = $pdo->prepare("SELECT COUNT(*) FROM services WHERE plan_id = :id");
            $stmt->execute(['id' => $id]);
            $count = $stmt->fetchColumn();
            
            if ($count > 0) {
                return response()->json(['success' => false, 'message' => 'این پلن دارای سرویس فعال است و نمی‌توان آن را حذف کرد!']);
            }
            
            $stmt = $pdo->prepare("DELETE FROM plans WHERE id = :id");
            $stmt->execute(['id' => $id]);
            
            return response()->json(['success' => true, 'message' => 'پلن با موفقیت حذف شد!']);
            
        } catch (\Exception $e) {
            return response()->json(['success' => false, 'message' => $e->getMessage()]);
        }
    }

    /**
     * دریافت لیست پلن‌ها به صورت JSON (API)
     */
    public function apiIndex()
    {
        if (!$this->botDatabaseExists()) {
            return response()->json(['success' => false, 'message' => 'دیتابیس ربات یافت نشد!'], 404);
        }

        try {
            $pdo = $this->getBotConnection();
            
            $stmt = $pdo->prepare("SELECT * FROM plans ORDER BY category, price");
            $stmt->execute();
            $plans = $stmt->fetchAll(\PDO::FETCH_ASSOC);
            
            // آمار هر پلن
            foreach ($plans as &$plan) {
                $stmt = $pdo->prepare("
                    SELECT COUNT(*) as total,
                           SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) as active
                    FROM services 
                    WHERE plan_id = :plan_id
                ");
                $stmt->execute(['plan_id' => $plan['id']]);
                $stats = $stmt->fetch(\PDO::FETCH_ASSOC);
                $plan['services_count'] = $stats['total'];
                $plan['active_services_count'] = $stats['active'];
            }
            
            return response()->json(['success' => true, 'data' => $plans]);
        } catch (\Exception $e) {
            return response()->json(['success' => false, 'message' => $e->getMessage()], 500);
        }
    }

    /**
     * دریافت جزئیات پلن به صورت JSON (API)
     */
    public function apiShow($id)
    {
        if (!$this->botDatabaseExists()) {
            return response()->json(['success' => false, 'message' => 'دیتابیس ربات یافت نشد!'], 404);
        }

        try {
            $pdo = $this->getBotConnection();
            
            $stmt = $pdo->prepare("SELECT * FROM plans WHERE id = :id");
            $stmt->execute(['id' => $id]);
            $plan = $stmt->fetch(\PDO::FETCH_ASSOC);
            
            if (!$plan) {
                return response()->json(['success' => false, 'message' => 'پلن یافت نشد!'], 404);
            }
            
            return response()->json(['success' => true, 'data' => $plan]);
        } catch (\Exception $e) {
            return response()->json(['success' => false, 'message' => $e->getMessage()], 500);
        }
    }
}

