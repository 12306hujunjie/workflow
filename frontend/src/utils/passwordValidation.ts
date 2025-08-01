/**
 * Password Validation Utilities
 * 
 * This file contains centralized password validation logic that is
 * EXACTLY synchronized with the backend validation rules.
 * 
 * Backend source: workflow_platform/bounded_contexts/user_management/presentation/schemas/user_schemas.py
 * Line 16: has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v)
 */

// Special characters exactly matching backend: "!@#$%^&*()_+-=[]{}|;:,.<>?"
const SPECIAL_CHARS_REGEX = /[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/;

/**
 * Validates password strength according to backend requirements
 */
export const validatePasswordStrength = (password: string): string | null => {
  if (password.length < 8) {
    return '密码长度至少需要8个字符';
  }
  if (!/[A-Z]/.test(password)) {
    return '密码需要包含至少一个大写字母';
  }
  if (!/[a-z]/.test(password)) {
    return '密码需要包含至少一个小写字母';
  }
  if (!/[0-9]/.test(password)) {
    return '密码需要包含至少一个数字';
  }
  if (!SPECIAL_CHARS_REGEX.test(password)) {
    return '密码需要包含至少一个特殊字符';
  }
  return null;
};

/**
 * Checks password strength for UI display
 */
export const checkPasswordStrength = (password: string): { 
  score: number; 
  text: string; 
  color: string;
  requirements: {
    length: boolean;
    lowercase: boolean;
    uppercase: boolean;
    digit: boolean;
    special: boolean;
  };
} => {
  const requirements = {
    length: password.length >= 8,
    lowercase: /[a-z]/.test(password),
    uppercase: /[A-Z]/.test(password),
    digit: /[0-9]/.test(password),
    special: SPECIAL_CHARS_REGEX.test(password),
  };

  const score = Object.values(requirements).filter(Boolean).length * 20;
  
  if (score < 100) {
    return { 
      score, 
      text: '不符合要求', 
      color: '#ff4d4f',
      requirements
    };
  }
  
  return { 
    score, 
    text: '符合要求', 
    color: '#52c41a',
    requirements
  };
};

/**
 * Advanced password strength validation for authService
 */
export const validatePasswordForService = (password: string): {
  score: number;
  feedback: string[];
  isValid: boolean;
} => {
  const feedback: string[] = [];
  let score = 0;

  // Length check
  if (password.length >= 8) {
    score += 1;
  } else {
    feedback.push('密码长度至少需要8个字符');
  }

  // Uppercase letter
  if (/[A-Z]/.test(password)) {
    score += 1;
  } else {
    feedback.push('密码需要包含至少一个大写字母');
  }

  // Lowercase letter
  if (/[a-z]/.test(password)) {
    score += 1;
  } else {
    feedback.push('密码需要包含至少一个小写字母');
  }

  // Digit
  if (/\d/.test(password)) {
    score += 1;
  } else {
    feedback.push('密码需要包含至少一个数字');
  }

  // Special character (exactly matching backend)
  if (SPECIAL_CHARS_REGEX.test(password)) {
    score += 1;
  } else {
    feedback.push('密码需要包含至少一个特殊字符');
  }

  return {
    score,
    feedback,
    isValid: score >= 5,
  };
};

/**
 * Gets the list of allowed special characters for display
 */
export const getAllowedSpecialChars = (): string => {
  return '!@#$%^&*()_+-=[]{}|;:,.<>?';
};

/**
 * Password strength level mapping
 */
export const getPasswordStrengthLevel = (score: number): {
  level: 'weak' | 'fair' | 'good' | 'strong';
  label: string;
  color: string;
} => {
  if (score <= 2) {
    return { level: 'weak', label: '弱', color: '#ef4444' };
  } else if (score === 3) {
    return { level: 'fair', label: '一般', color: '#f59e0b' };
  } else if (score === 4) {
    return { level: 'good', label: '良好', color: '#10b981' };
  } else {
    return { level: 'strong', label: '强', color: '#059669' };
  }
};