/**
 * Password Validation Tests
 * 
 * These tests ensure that frontend password validation is exactly
 * synchronized with backend validation rules.
 */

import { 
  validatePasswordStrength, 
  checkPasswordStrength, 
  validatePasswordForService,
  getAllowedSpecialChars,
  getPasswordStrengthLevel
} from '../passwordValidation';

describe('Password Validation', () => {
  describe('validatePasswordStrength', () => {
    it('should reject passwords shorter than 8 characters', () => {
      expect(validatePasswordStrength('Abc123!')).toBe('密码长度至少需要8个字符');
      expect(validatePasswordStrength('1234567')).toBe('密码长度至少需要8个字符');
    });

    it('should reject passwords without uppercase letters', () => {
      expect(validatePasswordStrength('abc123!@')).toBe('密码需要包含至少一个大写字母');
    });

    it('should reject passwords without lowercase letters', () => {
      expect(validatePasswordStrength('ABC123!@')).toBe('密码需要包含至少一个小写字母');
    });

    it('should reject passwords without digits', () => {
      expect(validatePasswordStrength('AbcDefg!')).toBe('密码需要包含至少一个数字');
    });

    it('should reject passwords without special characters', () => {
      expect(validatePasswordStrength('Abc12345')).toBe('密码需要包含至少一个特殊字符');
    });

    it('should accept valid passwords', () => {
      expect(validatePasswordStrength('Abc123!@')).toBeNull();
      expect(validatePasswordStrength('MySecure123$')).toBeNull();
      expect(validatePasswordStrength('Test1234#')).toBeNull();
    });

    it('should handle all backend special characters', () => {
      const specialChars = '!@#$%^&*()_+-=[]{}|;:,.<>?';
      for (const char of specialChars) {
        const password = `Test123${char}`;
        expect(validatePasswordStrength(password)).toBeNull();
      }
    });
  });

  describe('checkPasswordStrength', () => {
    it('should return correct score for weak passwords', () => {
      const result = checkPasswordStrength('abc');
      expect(result.score).toBe(20); // Only lowercase
      expect(result.text).toBe('不符合要求');
      expect(result.color).toBe('#ff4d4f');
    });

    it('should return correct score for strong passwords', () => {
      const result = checkPasswordStrength('Abc123!@');
      expect(result.score).toBe(100); // All requirements met
      expect(result.text).toBe('符合要求');
      expect(result.color).toBe('#52c41a');
    });

    it('should track individual requirements', () => {
      const result = checkPasswordStrength('Abc123!@');
      expect(result.requirements.length).toBe(true);
      expect(result.requirements.uppercase).toBe(true);
      expect(result.requirements.lowercase).toBe(true);
      expect(result.requirements.digit).toBe(true);
      expect(result.requirements.special).toBe(true);
    });
  });

  describe('validatePasswordForService', () => {
    it('should return detailed feedback for weak passwords', () => {
      const result = validatePasswordForService('abc');
      expect(result.score).toBe(1);
      expect(result.isValid).toBe(false);
      expect(result.feedback).toEqual([
        '密码长度至少需要8个字符',
        '密码需要包含至少一个大写字母',
        '密码需要包含至少一个数字',
        '密码需要包含至少一个特殊字符'
      ]);
    });

    it('should validate strong passwords', () => {
      const result = validatePasswordForService('Abc123!@');
      expect(result.score).toBe(5);
      expect(result.isValid).toBe(true);
      expect(result.feedback).toEqual([]);
    });
  });

  describe('getAllowedSpecialChars', () => {
    it('should return the exact backend special character set', () => {
      expect(getAllowedSpecialChars()).toBe('!@#$%^&*()_+-=[]{}|;:,.<>?');
    });
  });

  describe('getPasswordStrengthLevel', () => {
    it('should return correct levels for different scores', () => {
      expect(getPasswordStrengthLevel(1)).toEqual({
        level: 'weak',
        label: '弱',
        color: '#ef4444'
      });

      expect(getPasswordStrengthLevel(3)).toEqual({
        level: 'fair',
        label: '一般',
        color: '#f59e0b'
      });

      expect(getPasswordStrengthLevel(4)).toEqual({
        level: 'good',
        label: '良好',
        color: '#10b981'
      });

      expect(getPasswordStrengthLevel(5)).toEqual({
        level: 'strong',
        label: '强',
        color: '#059669'
      });
    });
  });

  describe('Backend Consistency Tests', () => {
    // Test cases that should exactly match backend behavior
    const testCases = [
      { password: 'Test123!', expected: null, description: 'Valid password with exclamation' },
      { password: 'Test123@', expected: null, description: 'Valid password with at symbol' },
      { password: 'Test123#', expected: null, description: 'Valid password with hash' },
      { password: 'Test123$', expected: null, description: 'Valid password with dollar' },
      { password: 'Test123%', expected: null, description: 'Valid password with percent' },
      { password: 'Test123^', expected: null, description: 'Valid password with caret' },
      { password: 'Test123&', expected: null, description: 'Valid password with ampersand' },
      { password: 'Test123*', expected: null, description: 'Valid password with asterisk' },
      { password: 'Test123(', expected: null, description: 'Valid password with open paren' },
      { password: 'Test123)', expected: null, description: 'Valid password with close paren' },
      { password: 'Test123_', expected: null, description: 'Valid password with underscore' },
      { password: 'Test123+', expected: null, description: 'Valid password with plus' },
      { password: 'Test123-', expected: null, description: 'Valid password with minus' },
      { password: 'Test123=', expected: null, description: 'Valid password with equals' },
      { password: 'Test123[', expected: null, description: 'Valid password with open bracket' },
      { password: 'Test123]', expected: null, description: 'Valid password with close bracket' },
      { password: 'Test123{', expected: null, description: 'Valid password with open brace' },
      { password: 'Test123}', expected: null, description: 'Valid password with close brace' },
      { password: 'Test123|', expected: null, description: 'Valid password with pipe' },
      { password: 'Test123;', expected: null, description: 'Valid password with semicolon' },
      { password: 'Test123:', expected: null, description: 'Valid password with colon' },
      { password: 'Test123,', expected: null, description: 'Valid password with comma' },
      { password: 'Test123.', expected: null, description: 'Valid password with period' },
      { password: 'Test123<', expected: null, description: 'Valid password with less than' },
      { password: 'Test123>', expected: null, description: 'Valid password with greater than' },
      { password: 'Test123?', expected: null, description: 'Valid password with question mark' },
    ];

    testCases.forEach(({ password, expected, description }) => {
      it(`should handle ${description}`, () => {
        expect(validatePasswordStrength(password)).toBe(expected);
      });
    });

    it('should reject passwords with invalid special characters', () => {
      // Characters not in the backend whitelist
      const invalidSpecialChars = ['~', '`', '"', '\'', '\\', '/'];
      
      invalidSpecialChars.forEach(char => {
        const password = `Test123${char}`;
        expect(validatePasswordStrength(password)).toBe('密码需要包含至少一个特殊字符');
      });
    });
  });
});