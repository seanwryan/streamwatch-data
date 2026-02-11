import { getDb, type Site, type Stats } from "@/lib/db";

export const dynamic = "force-dynamic";

async function getStats(): Promise<Stats | null> {
  try {
    const pool = getDb();
    const [sitesRes, samplesRes, volunteersRes] = await Promise.all([
      pool.query<{ count: string }>("SELECT COUNT(*) AS count FROM sites"),
      pool.query<{ count: string }>("SELECT COUNT(*) AS count FROM samples"),
      pool.query<{ count: string }>("SELECT COUNT(*) AS count FROM volunteers"),
    ]);
    return {
      sites: parseInt(sitesRes.rows[0]?.count ?? "0", 10),
      samples: parseInt(samplesRes.rows[0]?.count ?? "0", 10),
      volunteers: parseInt(volunteersRes.rows[0]?.count ?? "0", 10),
    };
  } catch {
    return null;
  }
}

async function getSites(): Promise<Site[]> {
  try {
    const pool = getDb();
    const result = await pool.query<Site>(
      `SELECT site_code, site_name, latitude, longitude, watershed
       FROM sites
       ORDER BY site_code
       LIMIT 100`
    );
    return result.rows;
  } catch {
    return [];
  }
}

export default async function Home() {
  const [stats, sites] = await Promise.all([getStats(), getSites()]);

  return (
    <div className="min-h-screen bg-zinc-50 font-sans dark:bg-zinc-950">
      <main className="mx-auto max-w-4xl px-6 py-12">
        <header className="mb-10">
          <h1 className="text-3xl font-bold tracking-tight text-zinc-900 dark:text-zinc-50">
            StreamWatch
          </h1>
          <p className="mt-1 text-zinc-600 dark:text-zinc-400">
            Watershed Institute · Monitoring data
          </p>
        </header>

        {stats ? (
          <section className="mb-10">
            <h2 className="mb-4 text-lg font-semibold text-zinc-800 dark:text-zinc-200">
              Database overview
            </h2>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
              <div className="rounded-lg border border-zinc-200 bg-white p-4 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
                <div className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">
                  {stats.sites.toLocaleString()}
                </div>
                <div className="text-sm text-zinc-600 dark:text-zinc-400">
                  Sites
                </div>
              </div>
              <div className="rounded-lg border border-zinc-200 bg-white p-4 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
                <div className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">
                  {stats.samples.toLocaleString()}
                </div>
                <div className="text-sm text-zinc-600 dark:text-zinc-400">
                  Samples
                </div>
              </div>
              <div className="rounded-lg border border-zinc-200 bg-white p-4 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
                <div className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">
                  {stats.volunteers.toLocaleString()}
                </div>
                <div className="text-sm text-zinc-600 dark:text-zinc-400">
                  Volunteers
                </div>
              </div>
            </div>
          </section>
        ) : (
          <section className="mb-10 rounded-lg border border-amber-200 bg-amber-50 p-4 dark:border-amber-900 dark:bg-amber-950/30">
            <p className="text-sm text-amber-800 dark:text-amber-200">
              Database not connected. Set DB_HOST, DB_NAME, DB_USER, DB_PASSWORD
              in .env.local (see .env.example).
            </p>
          </section>
        )}

        {sites.length > 0 ? (
          <section>
            <h2 className="mb-4 text-lg font-semibold text-zinc-800 dark:text-zinc-200">
              Sites (first 100)
            </h2>
            <div className="overflow-hidden rounded-lg border border-zinc-200 bg-white shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
              <table className="min-w-full divide-y divide-zinc-200 dark:divide-zinc-700">
                <thead>
                  <tr className="bg-zinc-50 dark:bg-zinc-800/50">
                    <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-zinc-600 dark:text-zinc-400">
                      Code
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-zinc-600 dark:text-zinc-400">
                      Name
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-zinc-600 dark:text-zinc-400">
                      Watershed
                    </th>
                    <th className="px-4 py-3 text-right text-xs font-medium uppercase tracking-wider text-zinc-600 dark:text-zinc-400">
                      Lat / Long
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-zinc-200 dark:divide-zinc-700">
                  {sites.map((site) => (
                    <tr
                      key={site.site_code}
                      className="hover:bg-zinc-50 dark:hover:bg-zinc-800/30"
                    >
                      <td className="whitespace-nowrap px-4 py-2 font-mono text-sm text-zinc-900 dark:text-zinc-100">
                        {site.site_code}
                      </td>
                      <td className="px-4 py-2 text-sm text-zinc-700 dark:text-zinc-300">
                        {site.site_name ?? "—"}
                      </td>
                      <td className="px-4 py-2 text-sm text-zinc-600 dark:text-zinc-400">
                        {site.watershed ?? "—"}
                      </td>
                      <td className="whitespace-nowrap px-4 py-2 text-right font-mono text-xs text-zinc-500 dark:text-zinc-500">
                        {site.latitude != null && site.longitude != null
                          ? `${Number(site.latitude).toFixed(4)}, ${Number(site.longitude).toFixed(4)}`
                          : "—"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        ) : stats === null ? null : (
          <section className="rounded-lg border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-900">
            <p className="text-sm text-zinc-600 dark:text-zinc-400">
              No sites loaded, or database not connected.
            </p>
          </section>
        )}
      </main>
    </div>
  );
}
