import { redirect } from 'next/navigation';

export default function UC1CalibrationRedirect({ params }: { params: { sessionId: string } }) {
  // Alias to the common calibration wizard
  redirect(`/sessions/${params.sessionId}/calibration`);
}
