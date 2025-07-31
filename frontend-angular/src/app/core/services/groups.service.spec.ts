import { TestBed } from '@angular/core/testing';
import {
  HttpClientTestingModule,
  HttpTestingController,
} from '@angular/common/http/testing';
import { of, throwError } from 'rxjs';

import { GroupsService } from './groups.service';
import { ErrorHandlerService } from './error-handler.service';
import { LoadingService } from './loading.service';
import { VKGroupResponse, VKGroupCreate, VKGroupUpdate } from '../models';

describe('GroupsService', () => {
  let service: GroupsService;
  let httpMock: HttpTestingController;
  let errorHandler: jasmine.SpyObj<ErrorHandlerService>;
  let loadingService: jasmine.SpyObj<LoadingService>;

  const mockGroup: VKGroupResponse = {
    id: 1,
    name: 'Test Group',
    screen_name: 'testgroup',
    description: 'Test description',
    members_count: 1000,
    is_closed: false,
    type: 'group',
    photo_100: 'http://example.com/photo100.jpg',
    photo_200: 'http://example.com/photo200.jpg',
    status: 'active',
    category: 'test',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    parsing_enabled: true,
    keywords_count: 5,
    comments_count: 10,
  };

  const mockGroupsResponse = {
    items: [mockGroup],
    total: 1,
    page: 1,
    size: 10,
  };

  beforeEach(() => {
    const errorHandlerSpy = jasmine.createSpyObj('ErrorHandlerService', [
      'handleError',
      'showSuccessNotification',
    ]);
    const loadingServiceSpy = jasmine.createSpyObj('LoadingService', [
      'show',
      'hide',
    ]);

    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [
        GroupsService,
        { provide: ErrorHandlerService, useValue: errorHandlerSpy },
        { provide: LoadingService, useValue: loadingServiceSpy },
      ],
    });

    service = TestBed.inject(GroupsService);
    httpMock = TestBed.inject(HttpTestingController);
    errorHandler = TestBed.inject(
      ErrorHandlerService
    ) as jasmine.SpyObj<ErrorHandlerService>;
    loadingService = TestBed.inject(
      LoadingService
    ) as jasmine.SpyObj<LoadingService>;
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('getGroups', () => {
    it('should fetch groups successfully', () => {
      service.getGroups().subscribe((response) => {
        expect(response).toEqual(mockGroupsResponse);
      });

      const req = httpMock.expectOne('/api/groups');
      expect(req.request.method).toBe('GET');
      req.flush(mockGroupsResponse);
    });

    it('should handle error when fetching groups', () => {
      const errorMessage = 'Failed to fetch groups';

      service.getGroups().subscribe({
        next: () => fail('should have failed'),
        error: (error) => {
          expect(error.message).toBe(errorMessage);
        },
      });

      const req = httpMock.expectOne('/api/groups');
      req.flush(
        { message: errorMessage },
        { status: 500, statusText: 'Internal Server Error' }
      );
    });

    it('should fetch groups with search parameters', () => {
      const params = { search: 'test', page: 2, size: 20 };

      service.getGroups(params).subscribe((response) => {
        expect(response).toEqual(mockGroupsResponse);
      });

      const req = httpMock.expectOne('/api/groups?search=test&page=2&size=20');
      expect(req.request.method).toBe('GET');
      req.flush(mockGroupsResponse);
    });
  });

  describe('getGroup', () => {
    it('should fetch single group successfully', () => {
      service.getGroup(1).subscribe((group) => {
        expect(group).toEqual(mockGroup);
      });

      const req = httpMock.expectOne('/api/groups/1');
      expect(req.request.method).toBe('GET');
      req.flush(mockGroup);
    });

    it('should handle error when fetching single group', () => {
      const errorMessage = 'Group not found';

      service.getGroup(999).subscribe({
        next: () => fail('should have failed'),
        error: (error) => {
          expect(error.message).toBe(errorMessage);
        },
      });

      const req = httpMock.expectOne('/api/groups/999');
      req.flush(
        { message: errorMessage },
        { status: 404, statusText: 'Not Found' }
      );
    });
  });

  describe('createGroup', () => {
    it('should create group successfully', () => {
      const newGroup: VKGroupCreate = {
        name: 'New Group',
        screen_name: 'newgroup',
      };

      service.createGroup(newGroup).subscribe((group) => {
        expect(group).toEqual(mockGroup);
      });

      const req = httpMock.expectOne('/api/groups');
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(newGroup);
      req.flush(mockGroup);
    });

    it('should handle validation error when creating group', () => {
      const invalidGroup: VKGroupCreate = {
        name: '',
        screen_name: '',
      };

      const errorMessage = 'Validation failed';

      service.createGroup(invalidGroup).subscribe({
        next: () => fail('should have failed'),
        error: (error) => {
          expect(error.message).toBe(errorMessage);
        },
      });

      const req = httpMock.expectOne('/api/groups');
      req.flush(
        { message: errorMessage },
        { status: 422, statusText: 'Unprocessable Entity' }
      );
    });
  });

  describe('updateGroup', () => {
    it('should update group successfully', () => {
      const updateData: VKGroupUpdate = {
        name: 'Updated Group Name',
        description: 'Updated description',
      };

      service.updateGroup(1, updateData).subscribe((group) => {
        expect(group).toEqual({ ...mockGroup, ...updateData });
      });

      const req = httpMock.expectOne('/api/groups/1');
      expect(req.request.method).toBe('PUT');
      expect(req.request.body).toEqual(updateData);
      req.flush({ ...mockGroup, ...updateData });
    });

    it('should handle error when updating non-existent group', () => {
      const updateData: VKGroupUpdate = { name: 'Updated Name' };
      const errorMessage = 'Group not found';

      service.updateGroup(999, updateData).subscribe({
        next: () => fail('should have failed'),
        error: (error) => {
          expect(error.message).toBe(errorMessage);
        },
      });

      const req = httpMock.expectOne('/api/groups/999');
      req.flush(
        { message: errorMessage },
        { status: 404, statusText: 'Not Found' }
      );
    });
  });

  describe('deleteGroup', () => {
    it('should delete group successfully', () => {
      service.deleteGroup(1).subscribe((response) => {
        expect(response).toBeUndefined();
      });

      const req = httpMock.expectOne('/api/groups/1');
      expect(req.request.method).toBe('DELETE');
      req.flush(null);
    });

    it('should handle error when deleting non-existent group', () => {
      const errorMessage = 'Group not found';

      service.deleteGroup(999).subscribe({
        next: () => fail('should have failed'),
        error: (error) => {
          expect(error.message).toBe(errorMessage);
        },
      });

      const req = httpMock.expectOne('/api/groups/999');
      req.flush(
        { message: errorMessage },
        { status: 404, statusText: 'Not Found' }
      );
    });
  });

  describe('bulkDeleteGroups', () => {
    it('should perform bulk delete successfully', () => {
      const groupIds = [1, 2, 3];

      service.bulkDeleteGroups(groupIds).subscribe((response) => {
        expect(response).toBeUndefined();
      });

      const req = httpMock.expectOne('/api/groups/bulk-delete');
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual({ ids: groupIds });
      req.flush(null);
    });

    it('should handle partial failure in bulk delete', () => {
      const groupIds = [1, 2, 3];
      const errorMessage = 'Some groups could not be deleted';

      service.bulkDeleteGroups(groupIds).subscribe({
        next: () => fail('should have failed'),
        error: (error) => {
          expect(error.message).toBe(errorMessage);
        },
      });

      const req = httpMock.expectOne('/api/groups/bulk-delete');
      req.flush(
        { message: errorMessage },
        { status: 400, statusText: 'Bad Request' }
      );
    });
  });
});
