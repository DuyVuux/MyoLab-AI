import React from 'react';
import { QueueItem } from '../types/qc-semantics';
import { assertNoFalseFinalState } from '../utils/qc-semantics';

interface QCCardProps {
  item: QueueItem;
}

export function QCCard({ item }: QCCardProps) {
  // Ensure the safety invariant is maintained before rendering
  assertNoFalseFinalState(item);

  return (
    <article
      className="qc-card border rounded-lg p-4 shadow-sm mb-4 bg-white"
      data-attention={item.attention}
      aria-label={`${item.label} for ${item.case_id}`}
    >
      <h2 className="text-lg font-semibold mb-2">{item.label}</h2>
      
      <div className="space-y-1 mb-4 text-sm">
        <p>
          <strong className="font-medium text-gray-700">Case:</strong>{' '}
          {item.case_id}
        </p>
        <p>
          <strong className="font-medium text-gray-700">Supportability:</strong>{' '}
          {item.supportability}
        </p>
        <p>
          <strong className="font-medium text-gray-700">Evaluation:</strong>{' '}
          {item.evaluation_status}
        </p>
      </div>

      <div className="mb-4">
        {item.reason_codes.length > 0 ? (
          <ul aria-label="Reason codes" className="list-disc list-inside space-y-1">
            {item.reason_codes.map((reason) => (
              <li key={reason} className="text-sm">
                <code className="bg-gray-100 px-1 py-0.5 rounded text-gray-800">
                  {reason}
                </code>
              </li>
            ))}
          </ul>
        ) : (
          <p data-reasons="none" className="text-sm text-gray-500 italic">
            No additional reason code supplied.
          </p>
        )}
      </div>

      <a
        href={`#case-${item.case_id}-evidence`}
        className="text-blue-600 hover:text-blue-800 text-sm font-medium underline"
      >
        Open evidence
      </a>
    </article>
  );
}
