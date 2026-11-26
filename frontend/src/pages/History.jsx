import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  History as HistoryIcon,
  Image as ImageIcon,
  FileText,
  Trash2,
  Eye,
  Search,
  Filter,
  AlertTriangle,
  ChevronLeft,
  ChevronRight,
  UploadCloud,
} from 'lucide-react';
import DashboardLayout from '../components/layout/DashboardLayout';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import StatusBadge from '../components/common/StatusBadge';
import Modal from '../components/common/Modal';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { getHistory, deleteHistoryItem } from '../services/api';

export const History = () => {
  const [items, setItems] = useState([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [typeFilter, setTypeFilter] = useState('all'); // all, image, document
  const [isLoading, setIsLoading] = useState(true);
  const [deleteModalItem, setDeleteModalItem] = useState(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const fetchItems = async (p = 1) => {
    setIsLoading(true);
    try {
      const data = await getHistory(p, 10);
      setItems(data.items || []);
      setPage(data.page || 1);
      setTotalPages(data.total_pages || 1);
      setTotalCount(data.total || 0);
    } catch (err) {
      console.error('Failed to load history:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchItems(page);
  }, [page]);

  const handleDeleteConfirm = async () => {
    if (!deleteModalItem) return;
    setIsDeleting(true);
    try {
      await deleteHistoryItem(deleteModalItem.id);
      setDeleteModalItem(null);
      await fetchItems(page);
    } catch (err) {
      console.error('Delete error:', err);
      alert('Failed to delete item: ' + (err.response?.data?.detail || err.message));
    } finally {
      setIsDeleting(false);
    }
  };

  const filteredItems = items.filter((item) => {
    const matchesSearch = item.original_filename.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = typeFilter === 'all' || item.file_type === typeFilter;
    return matchesSearch && matchesType;
  });

  return (
    <DashboardLayout>
      <div className="space-y-6 animate-fade-in">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
              Analysis History
            </h1>
            <p className="text-slate-500 text-sm mt-1">
              Review and revisit your previously uploaded images, signs, and documents.
            </p>
          </div>

          <Link to="/upload">
            <Button icon={UploadCloud}>New Upload</Button>
          </Link>
        </div>

        {/* Filters & Search */}
        <div className="flex flex-col sm:flex-row items-center gap-3 bg-white p-4 rounded-2xl border border-slate-200">
          <div className="relative flex-1 w-full">
            <Search className="w-5 h-5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" aria-hidden="true" />
            <input
              type="text"
              placeholder="Search by filename..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              aria-label="Search history by filename"
              className="w-full pl-10 pr-4 py-2 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <div className="flex items-center gap-2 w-full sm:w-auto">
            <Filter className="w-4 h-4 text-slate-400" aria-hidden="true" />
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              aria-label="Filter history by file type"
              className="px-3 py-2 border border-slate-200 rounded-xl text-sm bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="all">All Types</option>
              <option value="image">Images Only</option>
              <option value="document">Documents Only</option>
            </select>
          </div>
        </div>

        {/* History List */}
        <Card title={`All Records (${totalCount})`} icon={HistoryIcon}>
          {isLoading ? (
            <div className="py-16 text-center">
              <LoadingSpinner size="md" message="Loading your history..." />
            </div>
          ) : filteredItems.length > 0 ? (
            <div className="divide-y divide-slate-100">
              {filteredItems.map((item) => (
                <div
                  key={item.id}
                  className="py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-slate-50/70 p-3 rounded-xl transition-colors"
                >
                  <div className="flex items-start sm:items-center gap-3 min-w-0">
                    <div className="p-2.5 rounded-xl bg-slate-100 text-slate-600 shrink-0 mt-0.5 sm:mt-0">
                      {item.file_type === 'image' ? (
                        <ImageIcon className="w-5 h-5 text-blue-600" aria-hidden="true" />
                      ) : (
                        <FileText className="w-5 h-5 text-purple-600" aria-hidden="true" />
                      )}
                    </div>
                    <div className="min-w-0">
                      <h4 className="font-semibold text-slate-900 text-sm truncate">
                        {item.original_filename}
                      </h4>
                      <p className="text-xs text-slate-500 mt-0.5">
                        Uploaded on {new Date(item.upload_time).toLocaleString()} •{' '}
                        {(item.file_size / (1024 * 1024)).toFixed(2)} MB
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 self-end sm:self-auto shrink-0">
                    <StatusBadge status={item.status} />

                    <Link
                      to={
                        item.file_type === 'image'
                          ? `/image-analysis?id=${item.id}`
                          : `/document-analysis?id=${item.id}`
                      }
                    >
                      <Button variant="outline" size="sm" icon={Eye} ariaLabel={`View analysis for ${item.original_filename}`}>
                        View
                      </Button>
                    </Link>

                    <Button
                      variant="ghost"
                      size="sm"
                      icon={Trash2}
                      onClick={() => setDeleteModalItem(item)}
                      className="text-red-600 hover:bg-red-50 hover:text-red-700"
                      ariaLabel={`Delete ${item.original_filename}`}
                    />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="py-16 text-center space-y-3">
              <HistoryIcon className="w-12 h-12 text-slate-300 mx-auto" aria-hidden="true" />
              <h3 className="font-semibold text-slate-700">No records found</h3>
              <p className="text-sm text-slate-400 max-w-sm mx-auto">
                No history entries match your current search or filter criteria.
              </p>
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between">
              <span className="text-xs text-slate-500 font-medium">
                Page {page} of {totalPages}
              </span>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  icon={ChevronLeft}
                  disabled={page <= 1}
                  onClick={() => setPage((p) => Math.max(p - 1, 1))}
                  ariaLabel="Previous page"
                >
                  Previous
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  icon={ChevronRight}
                  iconPosition="right"
                  disabled={page >= totalPages}
                  onClick={() => setPage((p) => Math.min(p + 1, totalPages))}
                  ariaLabel="Next page"
                >
                  Next
                </Button>
              </div>
            </div>
          )}
        </Card>

        {/* Delete Confirmation Modal */}
        <Modal
          isOpen={!!deleteModalItem}
          onClose={() => setDeleteModalItem(null)}
          title="Delete History Record"
          footer={
            <>
              <Button variant="outline" onClick={() => setDeleteModalItem(null)}>
                Cancel
              </Button>
              <Button
                variant="danger"
                isLoading={isDeleting}
                onClick={handleDeleteConfirm}
              >
                Delete File & History
              </Button>
            </>
          }
        >
          <div className="space-y-3">
            <p className="text-sm text-slate-700">
              Are you sure you want to permanently delete{' '}
              <strong className="text-slate-900">{deleteModalItem?.original_filename}</strong>?
            </p>
            <p className="text-xs text-slate-500">
              This action will remove the uploaded file, generated explanations, and audio records
              from the system. This cannot be undone.
            </p>
          </div>
        </Modal>
      </div>
    </DashboardLayout>
  );
};
export default History;

