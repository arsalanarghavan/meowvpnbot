<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

class PanelController extends Controller
{
    private $dbPath;

    public function __construct()
    {
        $this->dbPath = base_path('../vpn_bot.db');
    }

    /**
     * نمایش لیست پنل‌ها
     */
    public function index()
    {
        if (!file_exists($this->dbPath)) {
            return redirect()->back()->with('error', 'دیتابیس ربات یافت نشد!');
        }

        $pdo = new \PDO("sqlite:{$this->dbPath}");
        
        $panels = $pdo->query("SELECT * FROM panels ORDER BY priority, id")->fetchAll(\PDO::FETCH_ASSOC);
        
        return view('panels.index', compact('panels'));
    }

    /**
     * نمایش فرم ایجاد پنل جدید
     */
    public function create()
    {
        return view('panels.create');
    }

    /**
     * ذخیره پنل جدید
     */
    public function store(Request $request)
    {
        $request->validate([
            'name' => 'required|max:100',
            'panel_type' => 'required|in:marzban,hiddify',
            'api_base_url' => 'required|url|max:255',
            'username' => 'required|max:100',
            'password' => 'required|max:100',
        ]);

        if (!file_exists($this->dbPath)) {
            return redirect()->back()->with('error', 'دیتابیس ربات یافت نشد!');
        }

        try {
            $pdo = new \PDO("sqlite:{$this->dbPath}");
            
            $stmt = $pdo->prepare("
                INSERT INTO panels (name, panel_type, api_base_url, username, password, is_active)
                VALUES (:name, :panel_type, :api_base_url, :username, :password, 1)
            ");
            
            $stmt->execute([
                'name' => $request->name,
                'panel_type' => $request->panel_type,
                'api_base_url' => rtrim($request->api_base_url, '/'),
                'username' => $request->username,
                'password' => $request->password,
            ]);
            
            return redirect()->route('panels.index')->with('success', 'پنل با موفقیت ایجاد شد!');
            
        } catch (\Exception $e) {
            return redirect()->back()->with('error', $e->getMessage());
        }
    }

    /**
     * نمایش فرم ویرایش پنل
     */
    public function edit($id)
    {
        if (!file_exists($this->dbPath)) {
            return redirect()->back()->with('error', 'دیتابیس ربات یافت نشد!');
        }

        $pdo = new \PDO("sqlite:{$this->dbPath}");
        
        $stmt = $pdo->prepare("SELECT * FROM panels WHERE id = :id");
        $stmt->execute(['id' => $id]);
        $panel = $stmt->fetch(\PDO::FETCH_ASSOC);
        
        if (!$panel) {
            return redirect()->back()->with('error', 'پنل یافت نشد!');
        }
        
        return view('panels.edit', compact('panel'));
    }

    /**
     * ویرایش پنل
     */
    public function update(Request $request, $id)
    {
        $request->validate([
            'name' => 'required|max:100',
            'panel_type' => 'required|in:marzban,hiddify',
            'api_base_url' => 'required|url|max:255',
            'username' => 'required|max:100',
            'password' => 'required|max:100',
        ]);

        if (!file_exists($this->dbPath)) {
            return redirect()->back()->with('error', 'دیتابیس ربات یافت نشد!');
        }

        try {
            $pdo = new \PDO("sqlite:{$this->dbPath}");
            
            $stmt = $pdo->prepare("
                UPDATE panels 
                SET name = :name,
                    panel_type = :panel_type,
                    api_base_url = :api_base_url,
                    username = :username,
                    password = :password
                WHERE id = :id
            ");
            
            $stmt->execute([
                'name' => $request->name,
                'panel_type' => $request->panel_type,
                'api_base_url' => rtrim($request->api_base_url, '/'),
                'username' => $request->username,
                'password' => $request->password,
                'id' => $id,
            ]);
            
            return redirect()->route('panels.index')->with('success', 'پنل با موفقیت ویرایش شد!');
            
        } catch (\Exception $e) {
            return redirect()->back()->with('error', $e->getMessage());
        }
    }

    /**
     * تغییر وضعیت پنل
     */
    public function toggleStatus($id)
    {
        if (!file_exists($this->dbPath)) {
            return response()->json(['success' => false, 'message' => 'دیتابیس یافت نشد!']);
        }

        try {
            $pdo = new \PDO("sqlite:{$this->dbPath}");
            
            $stmt = $pdo->prepare("
                UPDATE panels 
                SET is_active = CASE WHEN is_active = 1 THEN 0 ELSE 1 END 
                WHERE id = :id
            ");
            $stmt->execute(['id' => $id]);
            
            return response()->json(['success' => true, 'message' => 'وضعیت پنل تغییر کرد!']);
            
        } catch (\Exception $e) {
            return response()->json(['success' => false, 'message' => $e->getMessage()]);
        }
    }

    /**
     * حذف پنل
     */
    public function destroy($id)
    {
        if (!file_exists($this->dbPath)) {
            return response()->json(['success' => false, 'message' => 'دیتابیس یافت نشد!']);
        }

        try {
            $pdo = new \PDO("sqlite:{$this->dbPath}");
            
            $stmt = $pdo->prepare("DELETE FROM panels WHERE id = :id");
            $stmt->execute(['id' => $id]);
            
            return response()->json(['success' => true, 'message' => 'پنل با موفقیت حذف شد!']);
            
        } catch (\Exception $e) {
            return response()->json(['success' => false, 'message' => $e->getMessage()]);
        }
    }
}
