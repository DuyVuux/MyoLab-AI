import React from 'react';
import { QueueSummary } from '../types/qc-semantics';
import { QCCard } from './QCCard';

interface QCDashboardProps {
  summary: QueueSummary;
}

export function QCDashboard({ summary }: QCDashboardProps) {
  return (
    <main aria-labelledby="qc-dashboard-title" className="max-w-4xl mx-auto p-6 space-y-6">
      <aside 
        role="note" 
        aria-label="Research-only notice"
        className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded-r"
      >
        <p className="text-sm text-yellow-800">
          <strong className="font-semibold">RESEARCH ONLY</strong> — technical evidence review, not diagnosis.
        </p>
      </aside>

      <div>
        <h1 id="qc-dashboard-title" className="text-2xl font-bold text-gray-900 mb-2">
          Exception-first QC queue
        </h1>
        <p className="text-gray-600 text-sm">
          Order: FAIL/BLOCKED → WARNING/NEEDS_REVIEW → UNKNOWN/NOT_EVALUATED → PASS.
        </p>
      </div>

      {/* Summary statistics */}
      <section 
        aria-label="Queue Statistics" 
        className="grid grid-cols-2 md:grid-cols-4 gap-4"
      >
        {Object.entries(summary.counts).map(([attention, count]) => {
          if (count === 0) return null;
          return (
            <div key={attention} className="bg-gray-50 p-3 rounded border text-center">
              <div className="text-2xl font-bold">{count}</div>
              <div className="text-xs text-gray-500 uppercase tracking-wide">{attention}</div>
            </div>
          );
        })}
      </section>

      <section role="list" aria-label="QC cases" className="space-y-4">
        {summary.items.map((item) => (
          <QCCard key={item.case_id} item={item} />
        ))}
        {summary.items.length === 0 && (
          <p className="text-gray-500 text-center py-8">
            No cases in the queue.
          </p>
        )}
      </section>
    </main>
  );
}
