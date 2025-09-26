// Тест подключения к базам данных
import { Client } from 'pg';

describe('Database Connections', () => {
  test('PostgreSQL connection works', async () => {
    const client = new Client({
      connectionString: process.env.DATABASE_URL
    });

    await client.connect();
    const result = await client.query('SELECT 1 as test');
    expect(result.rows[0].test).toBe(1);
    await client.end();
  });

  test('Environment variables are set', () => {
    expect(process.env.DATABASE_URL).toBeDefined();
    expect(process.env.REDIS_URL).toBeDefined();
  });
});
