import { NextResponse } from "next/server";
import { getDb, type Site } from "@/lib/db";

export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const pool = getDb();
    const result = await pool.query<Site>(
      `SELECT site_code, site_name, latitude, longitude, watershed
       FROM sites
       ORDER BY site_code
       LIMIT 200`
    );
    return NextResponse.json(result.rows);
  } catch (err) {
    const message = err instanceof Error ? err.message : "Database error";
    console.error("GET /api/sites:", message);
    return NextResponse.json(
      { error: message },
      { status: 500 }
    );
  }
}
