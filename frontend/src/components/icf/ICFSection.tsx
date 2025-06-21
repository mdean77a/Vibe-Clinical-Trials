import React from 'react';

export interface ICFSectionData {
  name: string;
  title: string;
  content: string;
  status: 'pending' | 'generating' | 'ready_for_review' | 'approved' | 'error';
  wordCount?: number;
}

interface ICFSectionProps {
  section: ICFSectionData;
  isGenerating: boolean;
  onApprove?: (sectionName: string) => void;
  onEdit?: (sectionName: string, newContent: string) => void;
  onRegenerate?: (sectionName: string) => void;
}

const ICFSection: React.FC<ICFSectionProps> = ({
  section,
  isGenerating,
  onApprove,
  onEdit,
  onRegenerate,
}) => {
  const [isEditing, setIsEditing] = React.useState(false);
  const [editContent, setEditContent] = React.useState(section.content);

  React.useEffect(() => {
    setEditContent(section.content);
  }, [section.content]);

  const handleSaveEdit = () => {
    if (onEdit) {
      onEdit(section.name, editContent);
    }
    setIsEditing(false);
  };

  const handleCancelEdit = () => {
    setEditContent(section.content);
    setIsEditing(false);
  };

  const getStatusColor = () => {
    switch (section.status) {
      case 'pending': return '#94a3b8';
      case 'generating': return '#f59e0b';
      case 'ready_for_review': return '#3b82f6';
      case 'approved': return '#10b981';
      case 'error': return '#ef4444';
      default: return '#94a3b8';
    }
  };

  const getStatusIcon = () => {
    switch (section.status) {
      case 'pending': return '⏳';
      case 'generating': return '⚡';
      case 'ready_for_review': return '👁️';
      case 'approved': return '✅';
      case 'error': return '❌';
      default: return '⏳';
    }
  };

  return (
    <div style={{
      border: '1px solid #e5e7eb',
      borderRadius: '12px',
      padding: '24px',
      marginBottom: '24px',
      backgroundColor: '#ffffff',
      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
      transition: 'all 0.2s ease',
    }}>
      {/* Section Header */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '16px',
      }}>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <div style={{
            width: '32px',
            height: '32px',
            borderRadius: '8px',
            backgroundColor: getStatusColor(),
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginRight: '12px',
            color: 'white',
            fontSize: '16px',
          }}>
            {getStatusIcon()}
          </div>
          <div>
            <h3 style={{
              fontSize: '1.25rem',
              fontWeight: '600',
              color: '#1f2937',
              margin: 0,
            }}>
              {section.title}
            </h3>
            <p style={{
              fontSize: '0.875rem',
              color: '#6b7280',
              margin: 0,
            }}>
              {section.wordCount && `${section.wordCount} words • `}
              Status: {section.status === 'ready_for_review' ? 'Ready for Review' : section.status.charAt(0).toUpperCase() + section.status.slice(1).replace('_', ' ')}
            </p>
          </div>
        </div>

        {/* Action Buttons */}
        {(section.status === 'ready_for_review' || section.status === 'approved') && !isEditing && (
          <div style={{ display: 'flex', gap: '8px' }}>
            {section.status === 'ready_for_review' && (
              <button
                onClick={() => onApprove?.(section.name)}
                style={{
                  padding: '8px 16px',
                  fontSize: '0.875rem',
                  border: '1px solid #10b981',
                  borderRadius: '6px',
                  backgroundColor: '#10b981',
                  color: '#ffffff',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = '#059669';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = '#10b981';
                }}
              >
                ✓ Approve
              </button>
            )}
            <button
              onClick={() => setIsEditing(true)}
              style={{
                padding: '8px 16px',
                fontSize: '0.875rem',
                border: '1px solid #d1d5db',
                borderRadius: '6px',
                backgroundColor: '#ffffff',
                color: '#374151',
                cursor: 'pointer',
                transition: 'all 0.2s',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#f9fafb';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = '#ffffff';
              }}
            >
              ✏️ Edit
            </button>
            <button
              onClick={() => onRegenerate?.(section.name)}
              disabled={isGenerating}
              style={{
                padding: '8px 16px',
                fontSize: '0.875rem',
                border: '1px solid #d1d5db',
                borderRadius: '6px',
                backgroundColor: '#ffffff',
                color: '#374151',
                cursor: isGenerating ? 'not-allowed' : 'pointer',
                opacity: isGenerating ? 0.6 : 1,
                transition: 'all 0.2s',
              }}
              onMouseEnter={(e) => {
                if (!isGenerating) {
                  e.currentTarget.style.backgroundColor = '#f9fafb';
                }
              }}
              onMouseLeave={(e) => {
                if (!isGenerating) {
                  e.currentTarget.style.backgroundColor = '#ffffff';
                }
              }}
            >
              🔄 Regenerate
            </button>
          </div>
        )}
      </div>

      {/* Section Content */}
      <div style={{
        backgroundColor: '#f9fafb',
        border: '1px solid #e5e7eb',
        borderRadius: '8px',
        padding: '16px',
        minHeight: '120px',
      }}>
        {section.status === 'generating' && (
          <div>
            {section.content ? (
              // Show streaming content as it arrives
              <div style={{
                color: '#374151',
                lineHeight: '1.6',
                whiteSpace: 'pre-wrap',
                fontSize: '0.875rem',
                minHeight: '120px',
                position: 'relative',
              }}>
                {section.content}
                {/* Blinking cursor to show active generation */}
                <span style={{
                  display: 'inline-block',
                  width: '2px',
                  height: '1em',
                  backgroundColor: '#f59e0b',
                  marginLeft: '2px',
                  animation: 'blink 1s infinite',
                }}>|</span>
              </div>
            ) : (
              // Show loading state when no content yet
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                height: '120px',
                color: '#6b7280',
              }}>
                <div style={{
                  width: '24px',
                  height: '24px',
                  border: '2px solid #f3f4f6',
                  borderTop: '2px solid #f59e0b',
                  borderRadius: '50%',
                  animation: 'spin 1s linear infinite',
                  marginRight: '12px',
                }}></div>
                Generating {section.title.toLowerCase()}...
              </div>
            )}
          </div>
        )}

        {section.status === 'pending' && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            height: '120px',
            color: '#6b7280',
            fontStyle: 'italic',
          }}>
            Waiting to generate {section.title.toLowerCase()}...
          </div>
        )}

        {section.status === 'error' && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            height: '120px',
            color: '#ef4444',
          }}>
            ❌ Error generating {section.title.toLowerCase()}. Please try regenerating.
          </div>
        )}

        {(section.status === 'ready_for_review' || section.status === 'approved') && !isEditing && (
          <div style={{
            color: '#374151',
            lineHeight: '1.6',
            whiteSpace: 'pre-wrap',
            fontSize: '0.875rem',
          }}>
            {section.content || 'No content generated.'}
          </div>
        )}

        {(section.status === 'ready_for_review' || section.status === 'approved') && isEditing && (
          <div>
            <textarea
              value={editContent}
              onChange={(e) => setEditContent(e.target.value)}
              style={{
                width: '100%',
                minHeight: '200px',
                padding: '12px',
                border: '1px solid #d1d5db',
                borderRadius: '6px',
                fontSize: '0.875rem',
                fontFamily: 'inherit',
                lineHeight: '1.6',
                resize: 'vertical',
                outline: 'none',
                marginBottom: '12px',
              }}
              onFocus={(e) => {
                e.currentTarget.style.borderColor = '#8b5cf6';
                e.currentTarget.style.boxShadow = '0 0 0 3px rgba(139, 92, 246, 0.1)';
              }}
              onBlur={(e) => {
                e.currentTarget.style.borderColor = '#d1d5db';
                e.currentTarget.style.boxShadow = 'none';
              }}
            />
            <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
              <button
                onClick={handleCancelEdit}
                style={{
                  padding: '8px 16px',
                  fontSize: '0.875rem',
                  border: '1px solid #d1d5db',
                  borderRadius: '6px',
                  backgroundColor: '#ffffff',
                  color: '#374151',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = '#f9fafb';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = '#ffffff';
                }}
              >
                Cancel
              </button>
              <button
                onClick={handleSaveEdit}
                style={{
                  padding: '8px 16px',
                  fontSize: '0.875rem',
                  border: '1px solid #8b5cf6',
                  borderRadius: '6px',
                  backgroundColor: '#8b5cf6',
                  color: '#ffffff',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = '#7c3aed';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = '#8b5cf6';
                }}
              >
                Save Changes
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ICFSection;