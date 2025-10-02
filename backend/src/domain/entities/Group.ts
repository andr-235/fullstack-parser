/**
 * @fileoverview Group Entity - основная бизнес-сущность группы
 *
 * ENTITY ПРИНЦИПЫ:
 * - Имеет уникальный идентификатор
 * - Инкапсулирует бизнес-логику
 * - Защищает свои инварианты
 * - Валидация в конструкторе и методах
 * - Неизменяемость через приватные сеттеры
 */

import { GroupId } from '@domain/value-objects/GroupId';
import { VkId } from '@domain/value-objects/VkId';
import { GroupStatus } from '@domain/value-objects/GroupStatus';
import { InvariantViolationError, ValidationError } from '@domain/errors/DomainError';

/**
 * Параметры для создания Group entity
 */
export interface CreateGroupProps {
  readonly id?: GroupId; // Optional для новых групп
  readonly vkId: VkId;
  readonly name: string;
  readonly screenName: string | null;
  readonly photo50: string | null;
  readonly membersCount: number | null;
  readonly isClosed: 0 | 1 | 2;
  readonly description: string | null;
  readonly status: GroupStatus;
  readonly taskId: string;
  readonly uploadedAt?: Date;
}

/**
 * Group Entity - представляет группу ВКонтакте в системе
 *
 * @description
 * Основная бизнес-сущность для работы с группами.
 * Инкапсулирует всю логику валидации и бизнес-правил.
 *
 * Инварианты:
 * - VK ID должен быть уникальным
 * - Имя группы не может быть пустым
 * - Статус должен быть валидным
 * - Количество участников >= 0
 *
 * @example
 * ```typescript
 * const group = Group.create({
 *   vkId: VkId.create(123456),
 *   name: 'Test Group',
 *   screenName: 'testgroup',
 *   photo50: null,
 *   membersCount: 1000,
 *   isClosed: 0,
 *   description: 'Test description',
 *   status: GroupStatus.valid(),
 *   taskId: 'task-123'
 * });
 *
 * group.markAsInvalid('Group is banned');
 * console.log(group.status.isInvalid()); // true
 * ```
 */
export class Group {
  private readonly _id?: GroupId;
  private readonly _vkId: VkId;
  private _name: string;
  private _screenName: string | null;
  private _photo50: string | null;
  private _membersCount: number | null;
  private readonly _isClosed: 0 | 1 | 2;
  private _description: string | null;
  private _status: GroupStatus;
  private readonly _taskId: string;
  private readonly _uploadedAt: Date;

  private constructor(props: CreateGroupProps) {
    this._id = props.id;
    this._vkId = props.vkId;
    this._name = props.name;
    this._screenName = props.screenName;
    this._photo50 = props.photo50;
    this._membersCount = props.membersCount;
    this._isClosed = props.isClosed;
    this._description = props.description;
    this._status = props.status;
    this._taskId = props.taskId;
    this._uploadedAt = props.uploadedAt || new Date();

    this.validate();
  }

  /**
   * Создает новую группу
   *
   * @param props - параметры группы
   * @throws ValidationError если параметры невалидны
   */
  public static create(props: CreateGroupProps): Group {
    return new Group(props);
  }

  /**
   * Восстанавливает группу из БД (с ID)
   *
   * @param props - параметры группы из БД
   */
  public static restore(props: CreateGroupProps & { id: GroupId }): Group {
    return new Group(props);
  }

  /**
   * Валидация инвариантов entity
   *
   * @throws InvariantViolationError если инварианты нарушены
   */
  private validate(): void {
    // Имя группы не может быть пустым
    if (!this._name || this._name.trim().length === 0) {
      throw new InvariantViolationError(
        'Group name cannot be empty',
        'NON_EMPTY_NAME',
        { vkId: this._vkId.value }
      );
    }

    // Количество участников не может быть отрицательным
    if (this._membersCount !== null && this._membersCount < 0) {
      throw new InvariantViolationError(
        'Members count cannot be negative',
        'NON_NEGATIVE_MEMBERS',
        { vkId: this._vkId.value, membersCount: this._membersCount }
      );
    }

    // isClosed должен быть 0, 1 или 2
    if (![0, 1, 2].includes(this._isClosed)) {
      throw new InvariantViolationError(
        'isClosed must be 0, 1, or 2',
        'INVALID_IS_CLOSED',
        { vkId: this._vkId.value, isClosed: this._isClosed }
      );
    }
  }

  // ============ Геттеры ============

  public get id(): GroupId | undefined {
    return this._id;
  }

  public get vkId(): VkId {
    return this._vkId;
  }

  public get name(): string {
    return this._name;
  }

  public get screenName(): string | null {
    return this._screenName;
  }

  public get photo50(): string | null {
    return this._photo50;
  }

  public get membersCount(): number | null {
    return this._membersCount;
  }

  public get isClosed(): 0 | 1 | 2 {
    return this._isClosed;
  }

  public get description(): string | null {
    return this._description;
  }

  public get status(): GroupStatus {
    return this._status;
  }

  public get taskId(): string {
    return this._taskId;
  }

  public get uploadedAt(): Date {
    return this._uploadedAt;
  }

  // ============ Бизнес-методы ============

  /**
   * Помечает группу как невалидную
   *
   * @param reason - причина невалидности
   */
  public markAsInvalid(reason?: string): void {
    this._status = GroupStatus.invalid();

    if (reason) {
      this._description = `INVALID: ${reason}`;
    }
  }

  /**
   * Помечает группу как дубликат
   */
  public markAsDuplicate(): void {
    this._status = GroupStatus.duplicate();
  }

  /**
   * Помечает группу как валидную
   */
  public markAsValid(): void {
    this._status = GroupStatus.valid();
  }

  /**
   * Обновляет имя группы
   *
   * @param name - новое имя
   * @throws ValidationError если имя пустое
   */
  public updateName(name: string): void {
    if (!name || name.trim().length === 0) {
      throw new ValidationError(
        'Group name cannot be empty',
        { field: 'name' }
      );
    }

    this._name = name.trim();
  }

  /**
   * Обновляет количество участников
   *
   * @param count - количество участников
   * @throws ValidationError если количество отрицательное
   */
  public updateMembersCount(count: number | null): void {
    if (count !== null && count < 0) {
      throw new ValidationError(
        'Members count cannot be negative',
        { field: 'membersCount', value: count }
      );
    }

    this._membersCount = count;
  }

  /**
   * Обновляет описание группы
   */
  public updateDescription(description: string | null): void {
    this._description = description;
  }

  /**
   * Обновляет аватар группы
   */
  public updatePhoto(photo50: string | null): void {
    this._photo50 = photo50;
  }

  /**
   * Обновляет screen name
   */
  public updateScreenName(screenName: string | null): void {
    this._screenName = screenName;
  }

  // ============ Проверки состояния ============

  /**
   * Проверяет, является ли группа новой (без ID)
   */
  public isNew(): boolean {
    return this._id === undefined;
  }

  /**
   * Проверяет, сохранена ли группа в БД (есть ID)
   */
  public isPersisted(): boolean {
    return this._id !== undefined;
  }

  /**
   * Проверяет, валидна ли группа
   */
  public isValid(): boolean {
    return this._status.isValid();
  }

  /**
   * Проверяет, можно ли обрабатывать группу
   */
  public canBeProcessed(): boolean {
    return this._status.canBeProcessed();
  }

  /**
   * Проверяет, является ли группа закрытой
   */
  public isClosedGroup(): boolean {
    return this._isClosed === 1 || this._isClosed === 2;
  }

  /**
   * Проверяет, является ли группа открытой
   */
  public isOpenGroup(): boolean {
    return this._isClosed === 0;
  }

  /**
   * Получает URL группы ВКонтакте
   */
  public getVkUrl(): string {
    if (this._screenName) {
      return `https://vk.com/${this._screenName}`;
    }

    return `https://vk.com/club${this._vkId.toPositive()}`;
  }

  // ============ Сравнение ============

  /**
   * Сравнивает две группы по ID
   */
  public equals(other: Group): boolean {
    if (!(other instanceof Group)) {
      return false;
    }

    // Если обе группы имеют ID, сравниваем по ID
    if (this._id && other._id) {
      return this._id.equals(other._id);
    }

    // Иначе сравниваем по VK ID
    return this._vkId.equals(other._vkId);
  }

  /**
   * Сравнивает группы по VK ID
   */
  public hasSameVkId(other: Group): boolean {
    return this._vkId.equals(other._vkId);
  }

  // ============ Сериализация ============

  /**
   * Преобразует в plain object для сохранения в БД
   */
  public toPersistence(): {
    id?: number;
    vk_id: number;
    name: string;
    screen_name: string | null;
    photo_50: string | null;
    members_count: number | null;
    is_closed: number;
    description: string | null;
    status: string;
    task_id: string;
    uploaded_at: Date;
  } {
    return {
      id: this._id?.value,
      vk_id: this._vkId.value,
      name: this._name,
      screen_name: this._screenName,
      photo_50: this._photo50,
      members_count: this._membersCount,
      is_closed: this._isClosed,
      description: this._description,
      status: this._status.value,
      task_id: this._taskId,
      uploaded_at: this._uploadedAt
    };
  }

  /**
   * Преобразует в JSON для API ответов
   */
  public toJSON(): object {
    return {
      id: this._id?.value,
      vkId: this._vkId.value,
      name: this._name,
      screenName: this._screenName,
      photo50: this._photo50,
      membersCount: this._membersCount,
      isClosed: this._isClosed,
      description: this._description,
      status: this._status.value,
      taskId: this._taskId,
      uploadedAt: this._uploadedAt.toISOString(),
      vkUrl: this.getVkUrl()
    };
  }
}
