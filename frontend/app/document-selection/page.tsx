'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Card from '@/components/Card';
import Button from '@/components/Button';
import type { Protocol } from '@/types/protocol';

export default function DocumentTypeSelection() {
  const router = useRouter();
  const [selectedProtocol, setSelectedProtocol] = useState<Protocol | null>(null);

  useEffect(() => {
    // First try to get protocol from localStorage
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

  const handleInformedConsentClick = () => {
    if (selectedProtocol) {
      const params = new URLSearchParams({
        protocolId: selectedProtocol.id,
        studyAcronym: selectedProtocol.study_acronym
      });
      router.push(`/informed-consent?${params.toString()}`);
    }
  };

  const handleSiteChecklistClick = () => {
    if (selectedProtocol) {
      const params = new URLSearchParams({
        protocolId: selectedProtocol.id,
        studyAcronym: selectedProtocol.study_acronym
      });
      router.push(`/site-checklist?${params.toString()}`);
    }
  };

  const handleBackToProtocols = () => {
    router.push('/');
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
          Select Document Type
        </h1>
        <p style={{ color: '#6b7280', fontSize: '1.125rem' }}>
          Choose the type of document you want to generate
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
      
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
        gap: '24px',
        marginBottom: '32px'
      }}>
        <div 
          style={{ cursor: 'pointer', transition: 'all 0.2s' }}
          onClick={handleInformedConsentClick}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'translateY(-2px)';
            e.currentTarget.style.boxShadow = '0 10px 25px -5px rgba(0, 0, 0, 0.1)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'translateY(0)';
            e.currentTarget.style.boxShadow = 'none';
          }}
        >
          <Card>
            <div style={{
              padding: '32px',
              textAlign: 'center',
              background: 'white',
              border: '1px solid #d8b4fe',
              borderRadius: '12px',
              boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
            }}>
              <div style={{
                width: '64px',
                height: '64px',
                background: '#e9d5ff',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 16px'
              }}>
                <span style={{ color: '#8b5cf6', fontSize: '2rem' }}>📋</span>
              </div>
              <h3 style={{ fontSize: '1.25rem', fontWeight: 'bold', color: '#1f2937', marginBottom: '16px' }}>
                Informed Consent Form
              </h3>
              <Button 
                style={{
                  background: 'linear-gradient(to right, #8b5cf6, #7c3aed)',
                  color: 'white',
                  fontWeight: '600',
                  padding: '12px 24px',
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                  border: 'none',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  width: '100%'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'linear-gradient(to right, #7c3aed, #6d28d9)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'linear-gradient(to right, #8b5cf6, #7c3aed)';
                }}
              >
                Generate Consent Form
              </Button>
            </div>
          </Card>
        </div>

        <div 
          style={{ cursor: 'pointer', transition: 'all 0.2s' }}
          onClick={handleSiteChecklistClick}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'translateY(-2px)';
            e.currentTarget.style.boxShadow = '0 10px 25px -5px rgba(0, 0, 0, 0.1)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'translateY(0)';
            e.currentTarget.style.boxShadow = 'none';
          }}
        >
          <Card>
            <div style={{
              padding: '32px',
              textAlign: 'center',
              background: 'white',
              border: '1px solid #d8b4fe',
              borderRadius: '12px',
              boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
            }}>
              <div style={{
                width: '64px',
                height: '64px',
                background: '#ddd6fe',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 16px'
              }}>
                <span style={{ color: '#7c3aed', fontSize: '2rem' }}>✅</span>
              </div>
              <h3 style={{ fontSize: '1.25rem', fontWeight: 'bold', color: '#1f2937', marginBottom: '16px' }}>
                Site Initiation Checklist
              </h3>
              <Button 
                style={{
                  background: 'linear-gradient(to right, #7c3aed, #6d28d9)',
                  color: 'white',
                  fontWeight: '600',
                  padding: '12px 24px',
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                  border: 'none',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  width: '100%'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'linear-gradient(to right, #6d28d9, #5b21b6)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'linear-gradient(to right, #7c3aed, #6d28d9)';
                }}
              >
                Generate Site Checklist
              </Button>
            </div>
          </Card>
        </div>
      </div>

      <div style={{ textAlign: 'center' }}>
        <Button 
          onClick={handleBackToProtocols}
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
          ← Back to Protocol Selection
        </Button>
      </div>
    </div>
  );
}