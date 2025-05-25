"use client";

import { useState } from "react";
import UnifiedCertificateForm from "@/components/UnifiedCertificateForm";
import VerificationSection from "@/components/VerificationSection";
import CertificatePreview from "@/components/CertificatePreview";
import { Certificate } from "@/types/certificate";

export default function Home() {
  const [currentCertificate, setCurrentCertificate] =
    useState<Certificate | null>(null);

  return (
    <main className="min-h-screen bg-gray-900 py-8">
      <div className="container mx-auto px-4">
        <h1 className="text-3xl font-bold text-center mb-8 text-white">
          Smart Certificate Generator
        </h1>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="space-y-8">
            <UnifiedCertificateForm
              onCertificateGenerated={setCurrentCertificate}
            />
            <VerificationSection />
          </div>
          <div>
            <CertificatePreview certificate={currentCertificate} />
          </div>
        </div>
      </div>
    </main>
  );
}
