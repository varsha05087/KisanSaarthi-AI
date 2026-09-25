/**
 * Image Service for KisanSaarthi AI
 *
 * Provides utilities for photo selection, previews, and safe file resizing
 * before sending to backend vision APIs.
 */

/**
 * Convert a File object to an object URL for instant UI preview
 */
export function createPreviewUrl(file) {
  if (!file) return null;
  return URL.createObjectURL(file);
}

/**
 * Revoke object URL to avoid memory leaks
 */
export function revokePreviewUrl(url) {
  if (url && url.startsWith('blob:')) {
    URL.revokeObjectURL(url);
  }
}

/**
 * Validate image file type and size
 */
export function validateImage(file, maxMb = 15) {
  if (!file) return { valid: false, error: 'No file selected' };
  
  const validTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/heic', 'image/heif'];
  const isValidType = validTypes.includes(file.type) || file.type.startsWith('image/');
  
  if (!isValidType) {
    return { valid: false, error: 'Please choose a valid image file (JPG, PNG, WebP).' };
  }

  const isSizeOk = file.size <= maxMb * 1024 * 1024;
  if (!isSizeOk) {
    return { valid: false, error: `Image must be less than ${maxMb}MB.` };
  }

  return { valid: true, error: null };
}

/**
 * Format bytes into human-readable size for farmers
 */
export function formatFileSize(bytes) {
  if (!bytes) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
}
