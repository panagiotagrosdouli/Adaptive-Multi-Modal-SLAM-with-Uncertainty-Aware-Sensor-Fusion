import { motion } from "framer-motion";

const benchmarkRows = [
  ["EuRoC MH_01", "ORB-SLAM3", "pending", "pending", "pending"],
  ["TUM-VI room", "adaptive fusion", "pending", "pending", "pending"],
  ["KITTI odometry", "visual baseline", "pending", "pending", "pending"],
];

export default function Home() {
  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <section className="mx-auto flex max-w-6xl flex-col gap-10 px-6 py-20">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7 }}
          className="max-w-4xl"
        >
          <p className="mb-4 text-sm uppercase tracking-[0.35em] text-cyan-300">
            Uncertainty-aware robotics research
          </p>
          <h1 className="text-5xl font-semibold tracking-tight md:text-7xl">
            Adaptive Multi-Modal SLAM
          </h1>
          <p className="mt-6 max-w-3xl text-lg leading-8 text-slate-300">
            A research framework for studying online sensor reliability, adaptive
            information weighting, trajectory evaluation, and failure prediction in
            visual-inertial SLAM systems.
          </p>
        </motion.div>

        <div className="grid gap-6 md:grid-cols-3">
          {[
            ["Reliability", "Estimate visual and inertial trust from measurable frontend and IMU signals."],
            ["Fusion", "Map reliability to pseudo-precision weights for estimator-aware sensor weighting."],
            ["Evaluation", "Report ATE/RPE with explicit timestamp association and alignment conventions."],
          ].map(([title, body]) => (
            <article key={title} className="rounded-2xl border border-slate-800 bg-slate-900/70 p-6">
              <h2 className="text-xl font-semibold text-cyan-200">{title}</h2>
              <p className="mt-3 text-sm leading-6 text-slate-300">{body}</p>
            </article>
          ))}
        </div>

        <section className="rounded-3xl border border-slate-800 bg-slate-900/60 p-6">
          <h2 className="text-2xl font-semibold">Pipeline</h2>
          <div className="mt-6 grid gap-4 md:grid-cols-5">
            {["Sensors", "Reliability", "Adaptive weights", "SLAM backend", "Metrics"].map((item, index) => (
              <div key={item} className="rounded-xl bg-slate-800 p-4 text-center">
                <div className="text-sm text-slate-400">0{index + 1}</div>
                <div className="mt-2 font-medium">{item}</div>
              </div>
            ))}
          </div>
        </section>

        <section className="rounded-3xl border border-slate-800 bg-slate-900/60 p-6">
          <h2 className="text-2xl font-semibold">Benchmark status</h2>
          <p className="mt-2 text-sm text-slate-400">
            Values remain pending until produced by committed experiment configurations and metric files.
          </p>
          <div className="mt-6 overflow-x-auto">
            <table className="w-full border-collapse text-left text-sm">
              <thead className="text-slate-400">
                <tr>
                  <th className="border-b border-slate-700 py-3">Dataset</th>
                  <th className="border-b border-slate-700 py-3">Backend</th>
                  <th className="border-b border-slate-700 py-3">ATE</th>
                  <th className="border-b border-slate-700 py-3">RPE</th>
                  <th className="border-b border-slate-700 py-3">FPS</th>
                </tr>
              </thead>
              <tbody>
                {benchmarkRows.map((row) => (
                  <tr key={row[0]}>
                    {row.map((cell) => (
                      <td key={cell} className="border-b border-slate-800 py-3 text-slate-200">
                        {cell}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </section>
    </main>
  );
}
