/**
 * @fileoverview Unit тесты для VkId Value Object
 */

import { VkId } from '@domain/value-objects/VkId';
import { DomainError } from '@domain/errors/DomainError';

describe('VkId Value Object', () => {
  describe('create', () => {
    it('должен создать валидный VkId из положительного числа', () => {
      // Act
      const vkId = VkId.create(123456789);

      // Assert
      expect(vkId.value).toBe(123456789);
    });

    it('должен создать валидный VkId из отрицательного числа', () => {
      // Act
      const vkId = VkId.create(-123456789);

      // Assert
      expect(vkId.value).toBe(-123456789);
    });

    it('должен выбросить ошибку для нуля', () => {
      // Act & Assert
      expect(() => VkId.create(0)).toThrow(DomainError);
    });

    it('должен выбросить ошибку для NaN', () => {
      // Act & Assert
      expect(() => VkId.create(NaN)).toThrow(DomainError);
    });

    it('должен выбросить ошибку для Infinity', () => {
      // Act & Assert
      expect(() => VkId.create(Infinity)).toThrow(DomainError);
      expect(() => VkId.create(-Infinity)).toThrow(DomainError);
    });

    it('должен выбросить ошибку для дробного числа', () => {
      // Act & Assert
      expect(() => VkId.create(123.456)).toThrow(DomainError);
    });
  });

  describe('isValid', () => {
    it('должен вернуть true для валидного ID', () => {
      // Act & Assert
      expect(VkId.isValid(123456789)).toBe(true);
      expect(VkId.isValid(-123456789)).toBe(true);
    });

    it('должен вернуть false для невалидного ID', () => {
      // Act & Assert
      expect(VkId.isValid(0)).toBe(false);
      expect(VkId.isValid(NaN)).toBe(false);
      expect(VkId.isValid(Infinity)).toBe(false);
      expect(VkId.isValid(123.456)).toBe(false);
    });
  });

  describe('toPositive', () => {
    it('должен преобразовать положительный ID в положительный', () => {
      // Arrange
      const vkId = VkId.create(123456789);

      // Act
      const positive = vkId.toPositive();

      // Assert
      expect(positive.value).toBe(123456789);
    });

    it('должен преобразовать отрицательный ID в положительный', () => {
      // Arrange
      const vkId = VkId.create(-123456789);

      // Act
      const positive = vkId.toPositive();

      // Assert
      expect(positive.value).toBe(123456789);
    });

    it('должен вернуть новый объект', () => {
      // Arrange
      const vkId = VkId.create(123456789);

      // Act
      const positive = vkId.toPositive();

      // Assert
      expect(positive).not.toBe(vkId);
      expect(positive).toBeInstanceOf(VkId);
    });
  });

  describe('toNegative', () => {
    it('должен преобразовать положительный ID в отрицательный', () => {
      // Arrange
      const vkId = VkId.create(123456789);

      // Act
      const negative = vkId.toNegative();

      // Assert
      expect(negative.value).toBe(-123456789);
    });

    it('должен преобразовать отрицательный ID в отрицательный', () => {
      // Arrange
      const vkId = VkId.create(-123456789);

      // Act
      const negative = vkId.toNegative();

      // Assert
      expect(negative.value).toBe(-123456789);
    });
  });

  describe('equals', () => {
    it('должен вернуть true для равных VkId', () => {
      // Arrange
      const vkId1 = VkId.create(123456789);
      const vkId2 = VkId.create(123456789);

      // Act & Assert
      expect(vkId1.equals(vkId2)).toBe(true);
    });

    it('должен вернуть true для равных VkId с разными знаками', () => {
      // Arrange
      const vkId1 = VkId.create(123456789);
      const vkId2 = VkId.create(-123456789);

      // Act & Assert
      expect(vkId1.equals(vkId2)).toBe(true);
    });

    it('должен вернуть false для разных VkId', () => {
      // Arrange
      const vkId1 = VkId.create(123456789);
      const vkId2 = VkId.create(987654321);

      // Act & Assert
      expect(vkId1.equals(vkId2)).toBe(false);
    });
  });

  describe('toString', () => {
    it('должен вернуть строковое представление', () => {
      // Arrange
      const vkId = VkId.create(123456789);

      // Act
      const str = vkId.toString();

      // Assert
      expect(str).toBe('123456789');
    });

    it('должен работать с отрицательными числами', () => {
      // Arrange
      const vkId = VkId.create(-123456789);

      // Act
      const str = vkId.toString();

      // Assert
      expect(str).toBe('-123456789');
    });
  });

  describe('immutability', () => {
    it('должен быть immutable', () => {
      // Arrange
      const vkId = VkId.create(123456789);

      // Act & Assert
      expect(() => {
        (vkId as any).value = 999;
      }).toThrow();
    });

    it('не должен изменяться при вызове toPositive', () => {
      // Arrange
      const original = VkId.create(-123456789);

      // Act
      const positive = original.toPositive();

      // Assert
      expect(original.value).toBe(-123456789);
      expect(positive.value).toBe(123456789);
    });

    it('не должен изменяться при вызове toNegative', () => {
      // Arrange
      const original = VkId.create(123456789);

      // Act
      const negative = original.toNegative();

      // Assert
      expect(original.value).toBe(123456789);
      expect(negative.value).toBe(-123456789);
    });
  });

  describe('value equality', () => {
    it('два VkId с одинаковым значением должны быть равны', () => {
      // Arrange
      const vkId1 = VkId.create(123456789);
      const vkId2 = VkId.create(123456789);

      // Act & Assert
      expect(vkId1.equals(vkId2)).toBe(true);
      expect(vkId1.value).toBe(vkId2.value);
    });

    it('VkId должен быть равен самому себе', () => {
      // Arrange
      const vkId = VkId.create(123456789);

      // Act & Assert
      expect(vkId.equals(vkId)).toBe(true);
    });
  });
});
