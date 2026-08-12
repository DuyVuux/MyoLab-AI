import {ReviewCase} from '../../../../src/features/review-queue/ReviewCase';
function fixture(id:string){const attention=id.includes('FAIL')?'FAIL':id.includes('WARN')?'WARNING':id.includes('PASS')?'PASS':'UNKNOWN';return {case_id:id,review_state:'REVIEWING',attention,reason_codes:attention==='UNKNOWN'?['DISTRIBUTION_CONTEXT_UNKNOWN']:[]}}
export default function Page({params}:{params:{caseId:string}}){return <ReviewCase record={fixture(params.caseId)}/>}
