<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

class PlanController extends Controller
{
    private $dbPath;

    public function __construct()
    {
        $this->dbPath = base_path('../vpn_bot.db');
    }

    /**
     * نمایش لیست پلن‌ها
     */
    public function index()
    {
        if (!file_exists($this->dbPath)) {
            return redirect()->back()->with('error', 'دیتابیس ربات یافت نشد!');
        }

        $pdo = new \PDO("sqlite:{$this->dbPath}");
        
        $plans = $pdo->query("SELECT * FROM plans ORDER BY category, price")->fetchAll(\PDO::FETCH_ASSOC);
        
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

        if (!file_exists($this->dbPath)) {
            return redirect()->back()->with('error', 'دیتابیس ربات یافت نشد!');
        }

        try {
            $pdo = new \PDO("sqlite:{$this->dbPath}");
            
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
        if (!file_exists($this->dbPath)) {
            return redirect()->back()->with('error', 'دیتابیس ربات یافت نشد!');
        }

        $pdo = new \PDO("sqlite:{$this->dbPath}");
        
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

        if (!file_exists($this->dbPath)) {
            return redirect()->back()->with('error', 'دیتابیس ربات یافت نشد!');
        }

        try {
            $pdo = new \PDO("sqlite:{$this->dbPath}");
            
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
        if (!file_exists($this->dbPath)) {
            return response()->json(['success' => false, 'message' => 'دیتابیس یافت نشد!']);
        }

        try {
            $pdo = new \PDO("sqlite:{$this->dbPath}");
            
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
}
