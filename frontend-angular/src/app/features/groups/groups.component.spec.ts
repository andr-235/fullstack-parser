import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { of, throwError } from 'rxjs';
import { MatTableModule } from '@angular/material/table';
import { MatPaginatorModule, PageEvent } from '@angular/material/paginator';
import { MatSortModule, Sort } from '@angular/material/sort';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatMenuModule } from '@angular/material/menu';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatDialogModule } from '@angular/material/dialog';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

import { GroupsComponent } from './groups.component';
import { GroupsService } from '../../core/services/groups.service';
import { VKGroupResponse } from '../../core/models';
import { LoadingSpinnerComponent } from '../../shared/components/loading-spinner/loading-spinner.component';

describe('GroupsComponent', () => {
  let component: GroupsComponent;
  let fixture: ComponentFixture<GroupsComponent>;
  let groupsService: jasmine.SpyObj<GroupsService>;
  let router: jasmine.SpyObj<Router>;

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

  beforeEach(async () => {
    const groupsServiceSpy = jasmine.createSpyObj('GroupsService', [
      'getGroups',
      'deleteGroup',
      'toggleGroupActive',
      'refreshGroupInfo',
    ]);
    const routerSpy = jasmine.createSpyObj('Router', ['navigate']);

    await TestBed.configureTestingModule({
      imports: [
        ReactiveFormsModule,
        MatTableModule,
        MatPaginatorModule,
        MatSortModule,
        MatFormFieldModule,
        MatInputModule,
        MatButtonModule,
        MatIconModule,
        MatMenuModule,
        MatCheckboxModule,
        MatSnackBarModule,
        MatProgressSpinnerModule,
        MatCardModule,
        MatChipsModule,
        MatTooltipModule,
        MatDialogModule,
        BrowserAnimationsModule,
      ],
      declarations: [GroupsComponent, LoadingSpinnerComponent],
      providers: [
        { provide: GroupsService, useValue: groupsServiceSpy },
        { provide: Router, useValue: routerSpy },
      ],
    }).compileComponents();

    groupsService = TestBed.inject(
      GroupsService
    ) as jasmine.SpyObj<GroupsService>;
    router = TestBed.inject(Router) as jasmine.SpyObj<Router>;
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(GroupsComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should initialize with default values', () => {
    expect(component.groups).toEqual([]);
    expect(component.totalItems).toBe(0);
    expect(component.currentPage).toBe(0);
    expect(component.pageSize).toBe(25);
    expect(component.loading).toBe(false);
  });

  it('should load groups on init', () => {
    groupsService.getGroups.and.returnValue(of(mockGroupsResponse));

    component.ngOnInit();

    expect(groupsService.getGroups).toHaveBeenCalled();
    expect(component.groups).toEqual(mockGroupsResponse.items);
    expect(component.totalItems).toBe(mockGroupsResponse.total);
  });

  it('should handle page change', () => {
    groupsService.getGroups.and.returnValue(of(mockGroupsResponse));
    const pageEvent: PageEvent = {
      pageIndex: 1,
      pageSize: 20,
      length: 100,
    };

    component.onPageChange(pageEvent);

    expect(groupsService.getGroups).toHaveBeenCalledWith({ page: 2, size: 20 });
    expect(component.currentPage).toBe(1);
    expect(component.pageSize).toBe(20);
  });

  it('should delete group', () => {
    groupsService.deleteGroup.and.returnValue(of(undefined));
    groupsService.getGroups.and.returnValue(of(mockGroupsResponse));

    component.deleteGroup(1);

    expect(groupsService.deleteGroup).toHaveBeenCalledWith(1);
  });

  it('should toggle group active status', () => {
    groupsService.toggleGroupActive.and.returnValue(of(mockGroup));
    groupsService.getGroups.and.returnValue(of(mockGroupsResponse));

    component.toggleGroupActive(1, true);

    expect(groupsService.toggleGroupActive).toHaveBeenCalledWith(1, true);
  });

  it('should refresh group info', () => {
    groupsService.refreshGroupInfo.and.returnValue(of(mockGroup));
    groupsService.getGroups.and.returnValue(of(mockGroupsResponse));

    component.refreshGroup(1);

    expect(groupsService.refreshGroupInfo).toHaveBeenCalledWith(1);
  });

  it('should clean up subscriptions on destroy', () => {
    spyOn(component['destroy$'], 'next');
    spyOn(component['destroy$'], 'complete');

    component.ngOnDestroy();

    expect(component['destroy$'].next).toHaveBeenCalled();
    expect(component['destroy$'].complete).toHaveBeenCalled();
  });
});
