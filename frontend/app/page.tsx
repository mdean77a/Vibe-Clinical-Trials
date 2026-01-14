import React from 'react';
import { LoginLink, LogoutLink, RegisterLink } from "@kinde-oss/kinde-auth-nextjs/components";
import { getKindeServerSession } from "@kinde-oss/kinde-auth-nextjs/server";
import HomePageClient from '@/components/HomePageClient';

export default async function HomePage() {
  const { getUser, isAuthenticated } = getKindeServerSession();
  const user = await getUser();
  const isAuth = await isAuthenticated();
  return (
    <div style={{ 
      padding: '24px', 
      maxWidth: '1024px', 
      margin: '0 auto',
      minHeight: '100vh'
    }}>
      <div style={{ textAlign: 'center', marginBottom: '48px' }}>
        <h1 style={{
          fontSize: '2.5rem',
          fontWeight: 'bold',
          background: 'linear-gradient(to right, #2563eb, #9333ea)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text',
          marginBottom: '16px'
        }}>
          Clinical Trial Accelerator
        </h1>
        <p style={{ color: '#6b7280', fontSize: '1.125rem' }}>
          Streamline your clinical trial documentation with AI-powered document generation. Generate informed consent forms and site initiation checklists.
        </p>
        
        {/* Auth Buttons */}
        <div style={{ marginTop: '24px', display: 'flex', gap: '12px', justifyContent: 'center', alignItems: 'center' }}>
          {!isAuth ? (
            <>
              <LoginLink 
                style={{
                  padding: '10px 20px',
                  backgroundColor: '#2563eb',
                  color: 'white',
                  borderRadius: '6px',
                  textDecoration: 'none',
                  fontWeight: '500',
                  cursor: 'pointer',
                  border: 'none'
                }}
              >
                Sign in
              </LoginLink>
              <RegisterLink 
                style={{
                  padding: '10px 20px',
                  backgroundColor: '#e5e7eb',
                  color: '#1f2937',
                  borderRadius: '6px',
                  textDecoration: 'none',
                  fontWeight: '500',
                  cursor: 'pointer',
                  border: 'none'
                }}
              >
                Sign up
              </RegisterLink>
            </>
          ) : (
            <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
              <span style={{ color: '#6b7280' }}>
                Hello, {user?.given_name || user?.email}!
              </span>
              <LogoutLink 
                style={{
                  padding: '10px 20px',
                  backgroundColor: '#dc2626',
                  color: 'white',
                  borderRadius: '6px',
                  textDecoration: 'none',
                  fontWeight: '500',
                  cursor: 'pointer',
                  border: 'none'
                }}
              >
                Sign out
              </LogoutLink>
            </div>
          )}
        </div>
      </div>

      <HomePageClient />
    </div>
  );
}