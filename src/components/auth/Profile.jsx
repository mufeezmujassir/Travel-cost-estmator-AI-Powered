import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { User, Mail, Calendar, Edit, Save, X, Trash2, Shield, AlertTriangle, CreditCard, ArrowRight } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';
import UsageDashboard from '../subscription/UsageDashboard';

const Profile = ({ onBack }) => {
  const { user, updateProfile, deleteAccount, logout } = useAuth();
  const navigate = useNavigate();
  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleteConfirmation, setDeleteConfirmation] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);
  const [activeSection, setActiveSection] = useState('profile'); // 'profile' or 'subscription'
  const [formData, setFormData] = useState({
    name: user?.name || '',
    email: user?.email || '',
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    const result = await updateProfile(formData);
    
    if (result.success) {
      setIsEditing(false);
      toast.success('Profile updated successfully!');
    } else {
      toast.error(result.error || 'Failed to update profile');
    }
    
    setIsLoading(false);
  };

  const handleDeleteAccount = async () => {
    if (deleteConfirmation.toLowerCase() !== 'delete my account') {
      toast.error('Please type "delete my account" to confirm');
      return;
    }

    setIsDeleting(true);
    
    try {
      const result = await deleteAccount();
      
      if (result.success) {
        toast.success('Account deleted successfully!');
        setShowDeleteConfirm(false);
        setDeleteConfirmation('');
        
        // Redirect to home page after a brief delay
        setTimeout(() => {
          if (onBack) {
            onBack(); // This will navigate back to travel view
          }
          // Force reload to ensure clean state
          window.location.href = '/';
        }, 1500);
      } else {
        toast.error(result.error || 'Failed to delete account');
      }
    } catch (error) {
      toast.error('An error occurred while deleting your account');
    } finally {
      setIsDeleting(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const getInitials = (name) => {
    return name
      .split(' ')
      .map(word => word[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const resetDeleteConfirmation = () => {
    setShowDeleteConfirm(false);
    setDeleteConfirmation('');
    setIsDeleting(false);
  };

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-purple-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        {/* Header with Back Button */}
        <div className="text-center mb-8 relative">
          <button
            onClick={onBack}
            className="absolute left-0 top-1/2 transform -translate-y-1/2 flex items-center text-gray-600 hover:text-gray-800 transition-colors duration-200"
          >
            <X className="w-5 h-5 mr-2" />
            Back
          </button>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Account Settings
          </h1>
          <p className="text-gray-600 mt-2">Manage your profile and subscription</p>
        </div>

        {/* Section Tabs */}
        <div className="flex justify-center space-x-4 mb-8">
          <button
            onClick={() => setActiveSection('profile')}
            className={`px-6 py-3 rounded-xl font-semibold transition-all ${
              activeSection === 'profile'
                ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg'
                : 'bg-white text-gray-700 hover:bg-gray-50'
            }`}
          >
            <User className="w-4 h-4 inline mr-2" />
            Profile
          </button>
          <button
            onClick={() => setActiveSection('subscription')}
            className={`px-6 py-3 rounded-xl font-semibold transition-all ${
              activeSection === 'subscription'
                ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg'
                : 'bg-white text-gray-700 hover:bg-gray-50'
            }`}
          >
            <CreditCard className="w-4 h-4 inline mr-2" />
            Subscription
          </button>
        </div>

        {activeSection === 'profile' ? (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Sidebar */}
            <div className="lg:col-span-1">
              <div className="bg-white/80 backdrop-blur-lg rounded-2xl shadow-xl p-6 border border-white/60">
                <div className="text-center mb-6">
                  <div className="relative inline-block">
                    <div className="w-24 h-24 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg mx-auto mb-4">
                      <span className="text-white text-2xl font-bold">
                        {getInitials(user.name)}
                      </span>
                    </div>
                    <div className="absolute -bottom-2 -right-2 w-8 h-8 bg-green-500 rounded-full border-4 border-white flex items-center justify-center">
                      <div className="w-3 h-3 bg-white rounded-full"></div>
                    </div>
                  </div>
                  <h2 className="text-xl font-semibold text-gray-900">{user.name}</h2>
                  <p className="text-gray-500 text-sm">{user.email}</p>
                </div>

                <button
                  onClick={() => setIsEditing(true)}
                  className="w-full flex items-center justify-center px-4 py-3 text-gray-700 bg-blue-50 hover:bg-blue-100 hover:text-blue-600 rounded-xl transition-all duration-200 group border border-blue-200"
                >
                  <Edit className="w-5 h-5 mr-3 text-blue-600 group-hover:text-blue-700" />
                  Edit Profile
                </button>
              </div>
            </div>

            {/* Main Content */}
            <div className="lg:col-span-2">
            <div className="bg-white/80 backdrop-blur-lg rounded-2xl shadow-xl p-8 border border-white/60">
              {!isEditing ? (
                // View Mode
                <div className="space-y-8">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-xl p-6 border border-blue-100">
                      <div className="flex items-center mb-4">
                        <User className="w-6 h-6 text-blue-600 mr-3" />
                        <h3 className="text-lg font-semibold text-gray-900">Personal Information</h3>
                      </div>
                      <div className="space-y-3">
                        <div>
                          <label className="block text-sm font-medium text-gray-500">Full Name</label>
                          <p className="mt-1 text-lg font-semibold text-gray-900">{user.name}</p>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-500">Email Address</label>
                          <p className="mt-1 text-lg font-semibold text-gray-900">{user.email}</p>
                        </div>
                      </div>
                    </div>

                    <div className="bg-gradient-to-br from-green-50 to-blue-50 rounded-xl p-6 border border-green-100">
                      <div className="flex items-center mb-4">
                        <Calendar className="w-6 h-6 text-green-600 mr-3" />
                        <h3 className="text-lg font-semibold text-gray-900">Account Information</h3>
                      </div>
                      <div className="space-y-3">
                        <div>
                          <label className="block text-sm font-medium text-gray-500">Member Since</label>
                          <p className="mt-1 text-lg font-semibold text-gray-900">{formatDate(user.created_at)}</p>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-500">Status</label>
                          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800 mt-1">
                            Active
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Security Card */}
                  <div className="bg-gradient-to-br from-orange-50 to-red-50 rounded-xl p-6 border border-orange-100">
                    <div className="flex items-center mb-4">
                      <Shield className="w-6 h-6 text-orange-600 mr-3" />
                      <h3 className="text-lg font-semibold text-gray-900">Security</h3>
                    </div>
                    <p className="text-gray-600 mb-4">
                      Manage your account security and privacy settings.
                    </p>
                    <button
                      onClick={() => setShowDeleteConfirm(true)}
                      className="inline-flex items-center px-4 py-2 border border-red-300 text-sm font-medium rounded-lg text-red-700 bg-white hover:bg-red-50 transition-colors duration-200"
                    >
                      <Trash2 className="w-4 h-4 mr-2" />
                      Delete Account
                    </button>
                  </div>
                </div>
              ) : (
                // Edit Mode
                <form onSubmit={handleSubmit} className="space-y-8">
                  <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-xl p-6 border border-blue-100">
                    <h3 className="text-lg font-semibold text-gray-900 mb-6">Edit Profile Information</h3>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                          Full Name
                        </label>
                        <input
                          type="text"
                          name="name"
                          id="name"
                          value={formData.name}
                          onChange={handleChange}
                          className="w-full px-4 py-3 border border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                          placeholder="Enter your full name"
                        />
                      </div>
                      <div>
                        <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                          Email Address
                        </label>
                        <input
                          type="email"
                          name="email"
                          id="email"
                          value={formData.email}
                          onChange={handleChange}
                          className="w-full px-4 py-3 border border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                          placeholder="Enter your email address"
                        />
                      </div>
                    </div>

                    <div className="flex space-x-4 pt-6">
                      <button
                        type="submit"
                        disabled={isLoading}
                        className="flex items-center px-6 py-3 border border-transparent text-sm font-medium rounded-xl text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 transition-all duration-200 transform hover:-translate-y-0.5"
                      >
                        <Save className="w-4 h-4 mr-2" />
                        {isLoading ? 'Saving...' : 'Save Changes'}
                      </button>
                      <button
                        type="button"
                        onClick={() => {
                          setIsEditing(false);
                          setFormData({
                            name: user.name,
                            email: user.email,
                          });
                        }}
                        className="flex items-center px-6 py-3 border border-gray-300 text-sm font-medium rounded-xl text-gray-700 bg-white hover:bg-gray-50 transition-all duration-200"
                      >
                        <X className="w-4 h-4 mr-2" />
                        Cancel
                      </button>
                    </div>
                  </div>
                </form>
              )}
            </div>
            </div>
          </div>
        ) : (
          /* Subscription Section */
          <div className="max-w-4xl mx-auto">
            <UsageDashboard />
          </div>
        )}
      </div>

      {/* Enhanced Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 transform transition-all duration-300 scale-100">
            <div className="text-center">
              <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100 mb-4">
                <AlertTriangle className="h-6 w-6 text-red-600" />
              </div>
              <h3 className="text-lg font-bold text-gray-900 mb-2">Delete Account</h3>
              <p className="text-gray-600 mb-4">
                This action cannot be undone. This will permanently delete your account and remove all your data from our servers.
              </p>
              
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
                <p className="text-sm text-red-700 font-medium mb-2">
                  Please type <span className="font-bold">"delete my account"</span> to confirm:
                </p>
                <input
                  type="text"
                  value={deleteConfirmation}
                  onChange={(e) => setDeleteConfirmation(e.target.value)}
                  className="w-full px-3 py-2 border border-red-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500"
                  placeholder="delete my account"
                />
              </div>

              <div className="flex space-x-3">
                <button
                  onClick={resetDeleteConfirmation}
                  disabled={isDeleting}
                  className="flex-1 px-4 py-3 border border-gray-300 text-sm font-medium rounded-xl text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 transition-colors duration-200"
                >
                  Cancel
                </button>
                <button
                  onClick={handleDeleteAccount}
                  disabled={isDeleting || deleteConfirmation.toLowerCase() !== 'delete my account'}
                  className="flex-1 px-4 py-3 border border-transparent text-sm font-medium rounded-xl text-white bg-red-600 hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
                >
                  {isDeleting ? (
                    <div className="flex items-center justify-center">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Deleting...
                    </div>
                  ) : (
                    'Delete Account'
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Profile;