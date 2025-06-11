import React, { useState } from 'react';
import Card from '@/components/Card';

const TestPage: React.FC = () => {
  const [uploadedFileName, setUploadedFileName] = useState<string | null>(null);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setUploadedFileName(file.name);

      // Placeholder for sending the file to the backend
      const formData = new FormData();
      formData.append('file', file);

      try {
        const response = await fetch('/upload', {
          method: 'POST',
          body: formData,
        });

        if (response.ok) {
          console.log('File uploaded successfully');
        } else {
          console.error('File upload failed');
        }
      } catch (error) {
        console.error('Error uploading file:', error);
      }
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
