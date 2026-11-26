import React, { useState } from 'react';
import {
  FileText,
  BookOpen,
  Table as TableIcon,
  Image as ImageIcon,
  ChevronLeft,
  ChevronRight,
  List,
  Sparkles,
  Volume2,
} from 'lucide-react';
import Card from '../common/Card';
import Button from '../common/Button';

export const DocumentResults = ({
  results,
  onGenerateAudio,
  isAudioGenerating = false,
}) => {
  const [currentPageIndex, setCurrentPageIndex] = useState(0);

  if (!results) return null;

  const {
    total_pages = 1,
    pages = [],
    headings = [],
    tables = [],
    embedded_visuals = [],
    explanation,
    summary,
    mode = 'explain',
  } = results;

  const currentPage = pages[currentPageIndex] || pages[0] || { page: 1, text: '', headings: [] };

  return (
    <div className="space-y-6">
      {/* Primary Result Banner / Explanation */}
      <Card
        title="Document Accessibility Explanation"
        subtitle={`Mode: ${mode.toUpperCase()} — Structured Document Comprehension`}
        icon={Sparkles}
        badge={
          <span className="px-3 py-1 bg-indigo-50 text-indigo-700 text-xs font-bold rounded-full border border-indigo-200 uppercase">
            {mode} Mode
          </span>
        }
        actions={
          onGenerateAudio && (
            <Button
              variant="primary"
              size="sm"
              icon={Volume2}
              isLoading={isAudioGenerating}
              onClick={onGenerateAudio}
            >
              Narrate Audio
            </Button>
          )
        }
      >
        <div className="p-5 rounded-xl bg-slate-50 border border-slate-200 text-slate-800 text-base sm:text-lg leading-relaxed font-medium">
          {explanation || summary || 'No explanation available.'}
        </div>
      </Card>

      {/* Document Overview Summary Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="p-4 bg-white border border-slate-200 rounded-xl">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">Pages / Slides</span>
          <span className="text-2xl font-bold text-slate-900 mt-1 block">{total_pages}</span>
        </div>
        <div className="p-4 bg-white border border-slate-200 rounded-xl">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">Headings</span>
          <span className="text-2xl font-bold text-indigo-600 mt-1 block">{headings.length}</span>
        </div>
        <div className="p-4 bg-white border border-slate-200 rounded-xl">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">Tables</span>
          <span className="text-2xl font-bold text-emerald-600 mt-1 block">{tables.length}</span>
        </div>
        <div className="p-4 bg-white border border-slate-200 rounded-xl">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">Embedded Visuals</span>
          <span className="text-2xl font-bold text-purple-600 mt-1 block">{embedded_visuals.length}</span>
        </div>
      </div>

      {/* Main Document Content Explorer */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Table of Contents & Embedded Figures */}
        <div className="lg:col-span-1 space-y-6">
          {/* Headings */}
          {headings.length > 0 && (
            <Card title="Document Structure" icon={List}>
              <ul className="space-y-1.5 max-h-56 overflow-y-auto pr-1 text-sm">
                {headings.map((h, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-slate-700">
                    <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 mt-2 shrink-0" aria-hidden="true" />
                    <span className="font-medium text-xs sm:text-sm">{h}</span>
                  </li>
                ))}
              </ul>
            </Card>
          )}

          {/* Embedded Visuals */}
          {embedded_visuals.length > 0 && (
            <Card title={`Extracted Visuals (${embedded_visuals.length})`} icon={ImageIcon}>
              <div className="space-y-3 max-h-72 overflow-y-auto pr-1">
                {embedded_visuals.map((vis, idx) => (
                  <div key={idx} className="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-1.5">
                    <div className="flex items-center justify-between text-xs text-slate-500">
                      <span className="font-semibold text-purple-700">Figure {idx + 1}</span>
                      {vis.page && <span>Page {vis.page}</span>}
                    </div>
                    <p className="text-xs text-slate-700 leading-normal">
                      {vis.description || 'Embedded chart/illustration extracted.'}
                    </p>
                  </div>
                ))}
              </div>
            </Card>
          )}
        </div>

        {/* Right 2 Columns: Page-by-Page Text & Tables Viewer */}
        <div className="lg:col-span-2 space-y-6">
          <Card
            title={`Page Content — ${currentPageIndex + 1} of ${Math.max(pages.length, 1)}`}
            icon={BookOpen}
            actions={
              pages.length > 1 && (
                <div className="flex items-center gap-1.5">
                  <button
                    onClick={() => setCurrentPageIndex((prev) => Math.max(prev - 1, 0))}
                    disabled={currentPageIndex === 0}
                    aria-label="Previous page"
                    className="p-1.5 rounded-lg border border-slate-200 hover:bg-slate-100 disabled:opacity-40 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-indigo-500 cursor-pointer"
                  >
                    <ChevronLeft className="w-4 h-4" aria-hidden="true" />
                  </button>
                  <span className="text-xs font-semibold px-2 text-slate-600">
                    {currentPageIndex + 1} / {pages.length}
                  </span>
                  <button
                    onClick={() => setCurrentPageIndex((prev) => Math.min(prev + 1, pages.length - 1))}
                    disabled={currentPageIndex >= pages.length - 1}
                    aria-label="Next page"
                    className="p-1.5 rounded-lg border border-slate-200 hover:bg-slate-100 disabled:opacity-40 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-indigo-500 cursor-pointer"
                  >
                    <ChevronRight className="w-4 h-4" aria-hidden="true" />
                  </button>
                </div>
              )
            }
          >
            {/* Extracted Text */}
            <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl min-h-[160px] max-h-96 overflow-y-auto whitespace-pre-wrap font-sans text-sm sm:text-base text-slate-800 leading-relaxed">
              {currentPage.text || 'No textual content on this page.'}
            </div>

            {/* Extracted Tables on this page */}
            {tables.filter((t) => !t.page || t.page === currentPage.page).length > 0 && (
              <div className="mt-6 space-y-4">
                <h5 className="font-semibold text-slate-900 text-sm flex items-center gap-2">
                  <TableIcon className="w-4 h-4 text-emerald-600" aria-hidden="true" />
                  <span>Tables on this Page:</span>
                </h5>

                {tables
                  .filter((t) => !t.page || t.page === currentPage.page)
                  .map((tbl, tIdx) => (
                    <div key={tIdx} className="overflow-x-auto border border-slate-200 rounded-xl">
                      <table className="min-w-full divide-y divide-slate-200 text-xs sm:text-sm">
                        {tbl.headers && tbl.headers.length > 0 && (
                          <thead className="bg-slate-100">
                            <tr>
                              {tbl.headers.map((h, hIdx) => (
                                <th key={hIdx} className="px-3 py-2 text-left font-bold text-slate-700">
                                  {h}
                                </th>
                              ))}
                            </tr>
                          </thead>
                        )}
                        <tbody className="divide-y divide-slate-100 bg-white">
                          {tbl.rows?.map((row, rIdx) => (
                            <tr key={rIdx} className="hover:bg-slate-50">
                              {row.map((cell, cIdx) => (
                                <td key={cIdx} className="px-3 py-2 text-slate-700">
                                  {cell}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ))}
              </div>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
};
export default DocumentResults;

