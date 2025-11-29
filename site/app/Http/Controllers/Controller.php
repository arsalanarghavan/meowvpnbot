<?php

namespace App\Http\Controllers;

use Illuminate\Foundation\Auth\Access\AuthorizesRequests;
use Illuminate\Foundation\Bus\DispatchesJobs;
use Illuminate\Foundation\Validation\ValidatesRequests;
use Illuminate\Routing\Controller as BaseController;
use App\Helpers\DatabaseHelper;

class Controller extends BaseController
{
    use AuthorizesRequests, DispatchesJobs, ValidatesRequests;

    /**
     * Get PDO connection to bot database
     * 
     * @return \PDO
     * @throws \RuntimeException|\PDOException
     */
    protected function getBotConnection(): \PDO
    {
        return DatabaseHelper::getBotConnection();
    }

    /**
     * Get bot database path
     * 
     * @return string
     * @throws \RuntimeException
     */
    protected function getBotDatabasePath(): string
    {
        return DatabaseHelper::getBotDatabasePath();
    }

    /**
     * Check if bot database exists
     * 
     * @return bool
     */
    protected function botDatabaseExists(): bool
    {
        return DatabaseHelper::botDatabaseExists();
    }
}
