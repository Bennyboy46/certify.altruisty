"use client";

import { useState } from "react";
import { Certificate } from "@/types/certificate";

export default function UnifiedCertificateForm({
  onCertificateGenerated,
}: {
  onCertificateGenerated: (certificate: Certificate) => void;
}) {
  const [formData, setFormData] = useState<Partial<Certificate>>({});
  const [courseType, setCourseType] = useState("technical");
  const [includeAppreciation, setIncludeAppreciation] = useState(true);
  const [loadingCertificate, setLoadingCertificate] = useState(false);
  const [certificateId, setCertificateId] = useState<string | null>(null);

  // Certificate submission handler
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoadingCertificate(true);
    try {
      // 1. Get appreciation message from AI model
      const appreciationResponse = await fetch(
        "http://localhost:8001/api/generate-appreciation",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            course_type: courseType,
          }),
        }
      );
      if (!appreciationResponse.ok)
        throw new Error("Failed to generate appreciation message");
      const { appreciation_message } = await appreciationResponse.json();

      // 2. Build the certificate content (name and course from user, appreciation from AI)
      const generatedContent = appreciation_message;

      // 3. Submit certificate with generated content
      const response = await fetch(
        "http://localhost:8000/certificates/generate",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            ...formData,
            content: generatedContent,
          }),
        }
      );
      if (!response.ok) throw new Error("Failed to generate certificate");
      const data = await response.json();
      setFormData(data);
      setCertificateId(data.certificate_id);
      onCertificateGenerated(data);
      alert("Certificate generated successfully!");
    } catch {
      alert("Failed to generate certificate. Please try again.");
    } finally {
      setLoadingCertificate(false);
    }
  };

  // Download PDF handler
  const handleDownloadPDF = async () => {
    if (!certificateId) return;
    try {
      const response = await fetch(
        `http://localhost:8000/certificates/${certificateId}/pdf`
      );
      if (!response.ok) throw new Error("Failed to download PDF");
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `certificate_${certificateId}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch {
      alert("Failed to download PDF. Please try again.");
    }
  };

  return (
    <div className="bg-gray-800 rounded-lg shadow-md p-6 border border-gray-700">
      <h2 className="text-xl font-semibold mb-4 text-white">
        Certificate Generator
      </h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label
            htmlFor="recipient_name"
            className="block text-sm font-medium text-gray-300"
          >
            Recipient Name
          </label>
          <input
            type="text"
            id="recipient_name"
            value={formData.recipient_name || ""}
            onChange={(e) =>
              setFormData({ ...formData, recipient_name: e.target.value })
            }
            className="mt-1 block w-full rounded-md bg-gray-700 border-gray-600 text-white placeholder-gray-400 focus:border-indigo-500 focus:ring-indigo-500"
            required
          />
        </div>
        <div>
          <label
            htmlFor="course_name"
            className="block text-sm font-medium text-gray-300"
          >
            Course Name
          </label>
          <input
            type="text"
            id="course_name"
            value={formData.course_name || ""}
            onChange={(e) =>
              setFormData({ ...formData, course_name: e.target.value })
            }
            className="mt-1 block w-full rounded-md bg-gray-700 border-gray-600 text-white placeholder-gray-400 focus:border-indigo-500 focus:ring-indigo-500"
            required
          />
        </div>
        <div>
          <label
            htmlFor="issue_date"
            className="block text-sm font-medium text-gray-300"
          >
            Issue Date
          </label>
          <input
            type="date"
            id="issue_date"
            value={formData.issue_date || ""}
            onChange={(e) =>
              setFormData({ ...formData, issue_date: e.target.value })
            }
            className="mt-1 block w-full rounded-md bg-gray-700 border-gray-600 text-white placeholder-gray-400 focus:border-indigo-500 focus:ring-indigo-500"
            required
          />
        </div>
        <div>
          <label
            htmlFor="courseType"
            className="block text-sm font-medium text-gray-300"
          >
            Course Type
          </label>
          <select
            id="courseType"
            value={courseType}
            onChange={(e) => setCourseType(e.target.value)}
            className="mt-1 block w-full rounded-md bg-gray-700 border-gray-600 text-white focus:border-indigo-500 focus:ring-indigo-500"
          >
            <option value="technical">Technical</option>
            <option value="academic">Academic</option>
            <option value="professional">Professional</option>
          </select>
        </div>
        <div className="flex items-center">
          <input
            type="checkbox"
            id="includeAppreciation"
            checked={includeAppreciation}
            onChange={(e) => setIncludeAppreciation(e.target.checked)}
            className="h-4 w-4 rounded border-gray-600 bg-gray-700 text-indigo-600 focus:ring-indigo-500"
          />
          <label
            htmlFor="includeAppreciation"
            className="ml-2 block text-sm text-gray-300"
          >
            Include Appreciation Message
          </label>
        </div>
        <div className="flex space-x-4">
          <button
            type="submit"
            disabled={loadingCertificate}
            className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors disabled:opacity-50"
          >
            {loadingCertificate ? "Generating..." : "Generate Certificate"}
          </button>
          <button
            type="button"
            onClick={handleDownloadPDF}
            disabled={!certificateId}
            className="flex-1 px-4 py-2 bg-emerald-600 text-white rounded-md hover:bg-emerald-700 transition-colors disabled:opacity-50"
          >
            Download PDF
          </button>
        </div>
      </form>
    </div>
  );
}
