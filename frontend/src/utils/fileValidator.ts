/**
 * Frontend File Validator (Section 29.8.6)
 *
 * Multi-layer validation mirroring backend FileValidator.
 * Runs before upload to catch issues early.
 */

const ALLOWED_TYPES: Record<string, string[]> = {
  document: [
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'image/png',
    'image/jpeg',
    'image/tiff',
    'image/bmp',
  ],
  audio: [
    'audio/webm',
    'audio/wav',
    'audio/mpeg',
    'audio/ogg',
    'audio/mp4',
  ],
};

const MAX_SIZES: Record<string, number> = {
  document: 50 * 1024 * 1024, // 50 MB
  audio: 25 * 1024 * 1024,    // 25 MB
};

const ALLOWED_EXTENSIONS: Record<string, string[]> = {
  document: ['.pdf', '.docx', '.png', '.jpg', '.jpeg', '.tiff', '.bmp'],
  audio: ['.webm', '.wav', '.mp3', '.ogg', '.m4a'],
};

// Magic bytes for file type verification
const MAGIC_BYTES: Record<string, number[]> = {
  'application/pdf': [0x25, 0x50, 0x44, 0x46],        // %PDF
  'image/png': [0x89, 0x50, 0x4e, 0x47],               // .PNG
  'image/jpeg': [0xff, 0xd8, 0xff],                     // JFIF
  'image/bmp': [0x42, 0x4d],                            // BM
};

export interface ValidationResult {
  valid: boolean;
  error?: string;
}

export function validateFile(file: File, context: 'document' | 'audio'): ValidationResult {
  // 1. Extension check
  const ext = '.' + file.name.split('.').pop()?.toLowerCase();
  if (!ALLOWED_EXTENSIONS[context]?.includes(ext)) {
    return {
      valid: false,
      error: `File type "${ext}" is not allowed. Allowed: ${ALLOWED_EXTENSIONS[context]?.join(', ')}`,
    };
  }

  // 2. MIME type check
  if (file.type && !ALLOWED_TYPES[context]?.includes(file.type)) {
    return {
      valid: false,
      error: `MIME type "${file.type}" is not allowed.`,
    };
  }

  // 3. Size check
  const maxSize = MAX_SIZES[context] || 50 * 1024 * 1024;
  if (file.size > maxSize) {
    const maxMB = Math.round(maxSize / 1024 / 1024);
    return {
      valid: false,
      error: `File too large (${Math.round(file.size / 1024 / 1024)}MB). Maximum: ${maxMB}MB.`,
    };
  }

  // 4. Empty file check
  if (file.size === 0) {
    return { valid: false, error: 'File is empty.' };
  }

  return { valid: true };
}

export async function validateFileMagicBytes(file: File): Promise<ValidationResult> {
  const slice = file.slice(0, 8);
  const buffer = await slice.arrayBuffer();
  const bytes = new Uint8Array(buffer);

  for (const [mime, magic] of Object.entries(MAGIC_BYTES)) {
    if (file.type === mime) {
      const matches = magic.every((b, i) => bytes[i] === b);
      if (!matches) {
        return {
          valid: false,
          error: 'File content does not match its extension. The file may be corrupted or renamed.',
        };
      }
    }
  }

  return { valid: true };
}
