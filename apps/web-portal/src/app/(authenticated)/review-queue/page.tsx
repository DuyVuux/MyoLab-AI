import {ReviewQueue} from '../../../src/features/review-queue/ReviewQueue';
const cases=[{case_id:'CASE-FAIL',attention:'FAIL'},{case_id:'CASE-WARN',attention:'WARNING'},{case_id:'CASE-UNKNOWN',attention:'UNKNOWN'},{case_id:'CASE-PASS',attention:'PASS'}];
export default function Page(){return <ReviewQueue cases={cases}/>}
