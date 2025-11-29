<?php

namespace App\Helpers;

use PDO;
use PDOException;

class DatabaseHelper
{
    /**
     * Get the bot database path
     * 
     * Priority:
     * 1. BOT_DATABASE_PATH environment variable
     * 2. Relative path from Laravel base_path
     * 3. Try to detect from project structure
     * 
     * @return string
     * @throws \RuntimeException
     */
    public static function getBotDatabasePath(): string
    {
        // First, try environment variable
        $dbPath = env('BOT_DATABASE_PATH');
        if ($dbPath && file_exists($dbPath)) {
            return $dbPath;
        }

        // Second, try relative path from Laravel base_path (default)
        $relativePath = base_path('../vpn_bot.db');
        if (file_exists($relativePath)) {
            return $relativePath;
        }

        // Third, try absolute path detection
        $basePath = base_path();
        $possiblePaths = [
            dirname($basePath) . '/vpn_bot.db',  // One level up
            $basePath . '/../vpn_bot.db',        // Relative from site/
            '/var/www/meowvpnbot/vpn_bot.db',    // Server default
        ];

        foreach ($possiblePaths as $path) {
            if (file_exists($path)) {
                return $path;
            }
        }

        throw new \RuntimeException(
            'Bot database file not found. Please set BOT_DATABASE_PATH in your .env file. ' .
            'Example: BOT_DATABASE_PATH=/var/www/meowvpnbot/vpn_bot.db'
        );
    }

    /**
     * Get PDO connection to bot database
     * 
     * @return PDO
     * @throws PDOException
     */
    public static function getBotConnection(): PDO
    {
        $dbPath = self::getBotDatabasePath();
        
        try {
            $pdo = new PDO("sqlite:{$dbPath}");
            $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
            $pdo->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
            
            // Enable foreign keys
            $pdo->exec('PRAGMA foreign_keys = ON');
            
            return $pdo;
        } catch (PDOException $e) {
            throw new PDOException(
                "Failed to connect to bot database at {$dbPath}: " . $e->getMessage(),
                (int)$e->getCode(),
                $e
            );
        }
    }

    /**
     * Check if bot database exists
     * 
     * @return bool
     */
    public static function botDatabaseExists(): bool
    {
        try {
            $dbPath = self::getBotDatabasePath();
            return file_exists($dbPath) && is_readable($dbPath);
        } catch (\RuntimeException $e) {
            return false;
        }
    }
}

