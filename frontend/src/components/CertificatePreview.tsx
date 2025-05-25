"use client";

import { Certificate } from "@/types/certificate";

interface CertificatePreviewProps {
  certificate: Certificate | null;
}

export default function CertificatePreview({
  certificate,
}: CertificatePreviewProps) {
  const handleDownloadPDF = async () => {
    if (!certificate?.certificate_id) return;
    try {
      const response = await fetch(
        `http://localhost:8000/certificates/${certificate.certificate_id}/pdf`
      );
      if (!response.ok) throw new Error("Failed to download PDF");
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `certificate_${certificate.certificate_id}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error("Failed to download PDF:", error);
      alert("Failed to download PDF. Please try again.");
    }
  };

  if (!certificate) {
    return (
      <div className="bg-gray-800 rounded-lg shadow-md p-6 border border-gray-700">
        <h2 className="text-xl font-semibold mb-4 text-white">
          Certificate Preview
        </h2>
        <div className="border-2 border-dashed border-gray-600 rounded-lg p-8 text-center text-gray-400">
          Generate a certificate to see the preview
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg shadow-md p-6 border border-gray-700">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold text-white">
          Certificate Preview
        </h2>
        <button
          onClick={handleDownloadPDF}
          className="px-4 py-2 bg-emerald-600 text-white rounded-md hover:bg-emerald-700 transition-colors"
        >
          Download PDF
        </button>
      </div>
      <div className="border-2 border-gray-700 rounded-lg p-8 bg-gray-900">
        <div className="text-center">
          <h3 className="text-2xl font-bold mb-4 text-white">
            CERTIFICATE OF ACHIEVEMENT
          </h3>
          <p className="text-lg mb-2 text-gray-300">This is to certify that</p>
          <p className="text-xl font-bold mb-4 text-white">
            {certificate.recipient_name}
          </p>
          <p className="text-lg mb-2 text-gray-300">
            has successfully completed the course
          </p>
          <p className="text-xl font-bold mb-4 text-white">
            {certificate.course_name}
          </p>
          {certificate.content && (
            <div className="mt-4 mb-4">
              <p className="text-lg text-gray-300 whitespace-pre-line">
                {certificate.content}
              </p>
            </div>
          )}
          <p className="text-lg text-gray-300">
            Issued on:{" "}
            <span className="text-white">{certificate.issue_date}</span>
          </p>
          {certificate.qr_code && (
            <div className="mt-4 flex justify-center">
              <img
                src={`data:image/png;base64,${certificate.qr_code}`}
                alt="Certificate QR Code"
                className="w-32 h-32 bg-white p-2 rounded-lg"
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
