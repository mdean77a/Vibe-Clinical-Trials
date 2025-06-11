import React, { useState } from 'react';
import Card from '@/components/Card';

const TestPage: React.FC = () => {
  const [uploadedFileName, setUploadedFileName] = useState<string | null>(null);

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setUploadedFileName(file.name);
      // Here you would handle the file upload to the server or file system
    }
  };

  return (
    <div className="p-4 space-y-4">
      <h1 className="text-2xl font-bold mb-4">Clinical Trial Accelerator</h1>
      <Card>
        <input type="file" accept="application/pdf" onChange={handleFileUpload} />
      </Card>
      {uploadedFileName && (
        <Card>
          <p>Uploaded File: {uploadedFileName}</p>
        </Card>
      )}
    </div>
  );
};

export default TestPage;
