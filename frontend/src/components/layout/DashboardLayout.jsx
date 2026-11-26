import React from 'react';
import Navbar from './Navbar';
import Sidebar from './Sidebar';
import Footer from './Footer';

export const DashboardLayout = ({ children }) => {
  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900">
      <Navbar />
      <div className="flex-1 flex max-w-7xl w-full mx-auto">
        <Sidebar />
        <main
          id="main-content"
          tabIndex="-1"
          className="flex-1 p-4 sm:p-6 lg:p-8 overflow-y-auto focus:outline-none"
        >
          {children}
        </main>
      </div>
      <Footer />
    </div>
  );
};
export default DashboardLayout;

