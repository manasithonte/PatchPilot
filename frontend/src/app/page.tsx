"use client";

import { useState } from "react";

export default function Home() {
  const [repoUrl, setRepoUrl] = useState("");
  const [githubToken, setGithubToken] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [selectedPackages, setSelectedPackages] = useState<Record<string, boolean>>({});
  const [upgrading, setUpgrading] = useState(false);
  const [upgradeResult, setUpgradeResult] = useState<any>(null);

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!repoUrl) return;
    setLoading(true);
    setResult(null);
    setUpgradeResult(null);

    try {
      const res = await fetch("http://localhost:8000/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ repo_url: repoUrl, github_token: githubToken }),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || "Error analyzing repository");
      }
      setResult(data);

      const initialSelected: Record<string, boolean> = {};
      if (data.upgrade_plan) {
        data.upgrade_plan.forEach((item: any) => {
          initialSelected[item.dependency] = item.recommended;
        });
      }
      setSelectedPackages(initialSelected);
    } catch (err: any) {
      console.error(err);
      alert(err.message || "Error analyzing repository");
    } finally {
      setLoading(false);
    }
  };

  const executeUpgrade = async () => {
    if (!result || !result.upgrade_plan || result.upgrade_plan.length === 0) return;

    const planToExecute = result.upgrade_plan.filter((item: any) => selectedPackages[item.dependency]);
    if (planToExecute.length === 0) {
      alert("Please select at least one package to upgrade.");
      return;
    }

    setUpgrading(true);

    try {
      const res = await fetch("http://localhost:8000/api/upgrade", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          repo_url: result.repo_url,
          plan: planToExecute,
          github_token: githubToken,
        }),
      });
      const data = await res.json();
      setUpgradeResult(data);
    } catch (err) {
      console.error(err);
      alert("Error upgrading repository");
    } finally {
      setUpgrading(false);
    }
  };

  return (
    <main className="min-h-screen p-8 bg-slate-900 text-slate-50 font-sans">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Header */}
        <header className="text-center py-12">
          <h1 className="text-5xl font-extrabold tracking-tight bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent mb-4">
            PatchPilot
          </h1>
          <p className="text-lg text-slate-400 max-w-2xl mx-auto">
            Your Agentic AI Code Upgrade Assistant. Automate dependency upgrades & safely generate GitHub PRs.
          </p>
        </header>

        {/* Input Form */}
        <div className="glass-panel p-6 shadow-2xl">
          <form onSubmit={handleAnalyze} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">GitHub Repository URL</label>
              <input
                type="url"
                required
                placeholder="https://github.com/username/repo"
                className="w-full px-4 py-3 rounded-lg bg-slate-800 border border-slate-700 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors"
                value={repoUrl}
                onChange={(e) => setRepoUrl(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">GitHub Token (Optional)</label>
              <input
                type="password"
                placeholder="ghp_..."
                className="w-full px-4 py-3 rounded-lg bg-slate-800 border border-slate-700 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors"
                value={githubToken}
                onChange={(e) => setGithubToken(e.target.value)}
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 px-4 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold rounded-lg shadow-lg hover:shadow-xl transition-all flex items-center justify-center space-x-2 disabled:opacity-50"
            >
              {loading ? (
                <span>Analyzing Repository...</span>
              ) : (
                <span>Analyze Dependencies</span>
              )}
            </button>
          </form>
        </div>

        {/* Results Section */}
        {result && (
          <div className="glass-panel p-6 shadow-2xl space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div>
              <h2 className="text-2xl font-bold mb-4 text-white">Analysis Results</h2>
              <div className="grid gap-4 md:grid-cols-2">
                <div className="p-4 rounded-lg bg-slate-800 border border-slate-700">
                  <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wide">Total Dependencies</h3>
                  <p className="text-3xl font-bold text-white mt-2">{result.dependencies.length}</p>
                </div>
                <div className="p-4 rounded-lg bg-slate-800 border border-slate-700">
                  <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wide">Outdated</h3>
                  <p className="text-3xl font-bold text-rose-400 mt-2">
                    {result.dependencies.filter((d: any) => d.is_outdated).length}
                  </p>
                </div>
              </div>
            </div>

            {/* AI Upgrade Plan */}
            {result.upgrade_plan && result.upgrade_plan.length > 0 && (
              <div>
                <h3 className="text-xl font-bold mb-4 text-white">AI Dependency Analysis</h3>
                <div className="space-y-4">
                  {result.upgrade_plan.map((item: any, idx: number) => {
                    const isSelected = selectedPackages[item.dependency] || false;
                    return (
                      <div key={idx} className={`p-5 rounded-lg border flex flex-col space-y-3 transition-colors ${isSelected ? 'bg-slate-800 border-blue-500/50' : 'bg-slate-800/50 border-slate-700 opacity-70'}`}>
                        <div className="flex justify-between items-start">
                          <div className="flex items-start space-x-4">
                            <div className="pt-1">
                              <input
                                type="checkbox"
                                className="w-5 h-5 rounded border-slate-600 bg-slate-700 text-blue-500 hover:ring-2 hover:ring-blue-500 cursor-pointer"
                                checked={isSelected}
                                onChange={(e) => setSelectedPackages(prev => ({ ...prev, [item.dependency]: e.target.checked }))}
                              />
                            </div>
                            <div>
                              <h4 className="text-lg font-bold text-blue-400">{item.dependency}</h4>
                              <p className="text-sm text-slate-400">
                                {item.from_version} <span className="text-slate-500 mx-1">→</span> <span className="text-green-400 font-semibold">{item.to_version}</span>
                              </p>
                            </div>
                          </div>
                          <span className={`px-3 py-1 text-xs font-bold rounded-full ${item.risk_level === 'High' ? 'bg-rose-500/20 text-rose-400' :
                            item.risk_level === 'Medium' ? 'bg-amber-500/20 text-amber-400' :
                              item.risk_level === 'None' ? 'bg-blue-500/20 text-blue-400' :
                                'bg-emerald-500/20 text-emerald-400'
                            }`}>
                            {item.risk_level} Risk
                          </span>
                        </div>
                        <div className="pl-9 space-y-2">
                          <div className="bg-slate-900/50 p-3 rounded text-sm text-slate-300">
                            <strong className="text-slate-400">AI Reasoning:</strong> {item.reasoning}
                          </div>
                          <div className="bg-slate-900/50 p-3 rounded text-sm text-slate-300">
                            <strong className="text-slate-400">Breaking Changes check:</strong> {item.breaking_changes}
                          </div>
                        </div>
                      </div>
                    )
                  })}
                </div>

                {/* Execute Button */}
                <div className="pt-6 border-t border-slate-700 mt-6">
                  {upgradeResult ? (
                    <div className="p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-lg flex items-center justify-between">
                      <div>
                        <h4 className="text-emerald-400 font-bold">Success!</h4>
                        <p className="text-slate-300 text-sm">{upgradeResult.message}</p>
                      </div>
                      {upgradeResult.pr_url && (
                        <a
                          href={upgradeResult.pr_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="px-4 py-2 bg-emerald-500 text-white rounded font-semibold text-sm hover:bg-emerald-600 transition"
                        >
                          View Pull Request
                        </a>
                      )}
                    </div>
                  ) : (
                    <button
                      onClick={executeUpgrade}
                      disabled={upgrading}
                      className="w-full py-4 px-6 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold rounded-lg shadow-lg hover:shadow-xl transition-all disabled:opacity-50"
                    >
                      {upgrading ? "Applying Upgrades & Creating PR..." : "Execute AI Upgrade Plan"}
                    </button>
                  )}
                </div>
              </div>
            )}

            {result.upgrade_plan && result.upgrade_plan.length === 0 && (
              <div className="p-6 bg-slate-800 rounded-lg text-center border border-slate-700">
                <p className="text-xl text-emerald-400 font-semibold">🎉 No dependencies found in this repository!</p>
              </div>
            )}
          </div>
        )}
      </div>
    </main>
  );
}
