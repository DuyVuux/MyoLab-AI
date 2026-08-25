import type {AuditEvent} from "../../contracts/automation";
export function AuditTimeline({events}:{events:AuditEvent[]}){
 return <section><h3>Audit trail</h3>{events.length===0?<p>No audit events.</p>:<ol>{events.map(e=><li key={e.event_id}><time dateTime={e.timestamp}>{e.timestamp}</time> <strong>{e.event_type}</strong> {e.actor_type}</li>)}</ol>}</section>
}
