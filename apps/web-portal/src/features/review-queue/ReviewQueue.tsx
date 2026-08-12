import React from 'react';
export function ReviewQueue({cases}:{cases:any[]}){return <main><aside role="note"><strong>RESEARCH ONLY</strong> — technical review, not diagnosis.</aside><h1>Review queue</h1><ol>{cases.map(c=><li key={c.case_id} data-attention={c.attention}><a href={`/review-queue/${c.case_id}`}>{c.case_id} — {c.attention}</a></li>)}</ol></main>}
