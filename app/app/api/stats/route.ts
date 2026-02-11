import { NextResponse } from "next/server";
import { getDb, type Stats } from "@/lib/db";

export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const pool = getDb();
    const [sitesRes, samplesRes, volunteersRes] = await Promise.all([
      pool.query<{ count: string }>("SELECT COUNT(*) AS count FROM sites"),
      pool.query<{ count: string }>("SELECT COUNT(*) AS count FROM samples"),
      pool.query<{ count: string }>("SELECT COUNT(*) AS count FROM volunteers"),
    ]);
    const stats: Stats = {
      sites: parseInt(sitesRes.rows[0]?.count ?? "0", 10),
      samples: parseInt(samplesRes.rows[0]?.count ?? "0", 10),
      volunteers: parseInt(volunteersRes.rows[0]?.count ?? "0", 10),
    };
    return NextResponse.json(stats);
  } catch (err) {
    const message = err instanceof Error ? err.message : "Database error";
    console.error("GET /api/stats:", message);
    return NextResponse.json(
      { error: message },
      { status: 500 }
    );
  }
}
