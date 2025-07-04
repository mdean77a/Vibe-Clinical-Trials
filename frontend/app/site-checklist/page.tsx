'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Card from '@/components/Card';
import Button from '@/components/Button';
import { getProtocolId } from '@/types/protocol';
import type { Protocol } from '@/types/protocol';

export default function SiteChecklistPage() {
  const router = useRouter();
  const [selectedProtocol, setSelectedProtocol] = useState<Protocol | null>(null);

  useEffect(() => {
    // Get protocol from localStorage
    const savedProtocol = localStorage.getItem('selectedProtocol');
    if (savedProtocol) {
      try {
        setSelectedProtocol(JSON.parse(savedProtocol));
      } catch (error) {
        console.error('Error parsing selected protocol:', error);
        // Redirect back to home if no valid protocol
        router.push('/');
      }
    } else {
      // No protocol selected, redirect to home
      router.push('/');
    }
  }, [router]);

  const handleMakeChecklist = () => {
    alert('This is not yet implemented.');
  };

  const handleReturnToDocumentSelection = () => {
    if (selectedProtocol) {
      const protocolId = getProtocolId(selectedProtocol);
      const params = new URLSearchParams({
        protocolId: protocolId,
        studyAcronym: selectedProtocol.study_acronym
      });
      router.push(`/document-selection?${params.toString()}`);
    } else {
      router.push('/document-selection');
    }
  };

  if (!selectedProtocol) {
    return (
      <div style={{ 
        minHeight: '100vh', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        padding: '24px',
        maxWidth: '1024px',
        margin: '0 auto'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{
            width: '48px',
            height: '48px',
            border: '2px solid #d8b4fe',
            borderTop: '2px solid #8b5cf6',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            margin: '0 auto 16px'
          }}></div>
          <p style={{ color: '#6b7280' }}>Loading protocol...</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ 
      padding: '24px', 
      maxWidth: '1024px', 
      margin: '0 auto',
      minHeight: '100vh'
    }}>
      <div style={{ textAlign: 'center', marginBottom: '32px' }}>
        <h1 style={{
          fontSize: '2.5rem',
          fontWeight: 'bold',
          background: 'linear-gradient(to right, #2563eb, #9333ea)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text',
          marginBottom: '8px'
        }}>
          Site Initiation Checklist
        </h1>
        <p style={{ color: '#6b7280', fontSize: '1.125rem' }}>
          Generate comprehensive site initiation checklists
        </p>
      </div>
      
      <Card style={{ marginBottom: '24px' }}>
        <div style={{
          padding: '16px',
          background: 'linear-gradient(to right, #faf5ff, #f3e8ff)',
          border: '1px solid #d8b4fe',
          borderRadius: '12px',
          boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <div style={{
              width: '40px',
              height: '40px',
              background: '#e9d5ff',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginRight: '12px'
            }}>
              <span style={{ color: '#8b5cf6', fontWeight: '600', fontSize: '0.875rem' }}>
                {selectedProtocol.study_acronym.substring(0, 2).toUpperCase()}
              </span>
            </div>
            <div>
              <p style={{ color: '#7c3aed', fontWeight: '600' }}>
                {selectedProtocol.study_acronym}
              </p>
              <p style={{ color: '#6d28d9', fontSize: '0.875rem' }}>
                {selectedProtocol.protocol_title}
              </p>
            </div>
          </div>
        </div>
      </Card>

      <Card>
        <div style={{
          padding: '48px',
          textAlign: 'center',
          background: 'white',
          border: '1px solid #e5e7eb',
          borderRadius: '12px'
        }}>
          <div style={{
            width: '80px',
            height: '80px',
            background: '#ddd6fe',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 24px'
          }}>
            <span style={{ color: '#7c3aed', fontSize: '2.5rem' }}>✅</span>
          </div>
          
          <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#1f2937', marginBottom: '16px' }}>
            Coming Soon
          </h2>
          
          <p style={{ color: '#6b7280', marginBottom: '32px', maxWidth: '600px', margin: '0 auto 32px' }}>
            The Site Initiation Checklist feature is currently under development. 
            This will generate comprehensive checklists to ensure all necessary steps 
            are completed before initiating a clinical trial at your site.
          </p>

          <div style={{ display: 'flex', gap: '16px', justifyContent: 'center' }}>
            <Button 
              onClick={handleMakeChecklist}
              style={{
                background: 'linear-gradient(to right, #d1d5db, #9ca3af)',
                color: 'white',
                fontWeight: '600',
                padding: '12px 24px',
                borderRadius: '8px',
                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                border: 'none',
                cursor: 'not-allowed',
                opacity: 0.6
              }}
              disabled
            >
              Generate Checklist (Coming Soon)
            </Button>
            
            <Button 
              onClick={handleReturnToDocumentSelection}
              style={{
                background: 'linear-gradient(to right, #6b7280, #4b5563)',
                color: 'white',
                fontWeight: '600',
                padding: '12px 24px',
                borderRadius: '8px',
                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                border: 'none',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'linear-gradient(to right, #4b5563, #374151)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'linear-gradient(to right, #6b7280, #4b5563)';
              }}
            >
              ← Back to Document Selection
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}