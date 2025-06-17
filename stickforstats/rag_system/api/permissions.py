from rest_framework import permissions

class IsDocumentOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of documents or admin users to manage them.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to anyone
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Admin users can do anything
        if request.user.is_staff:
            return True
            
        # Document owners can edit their own documents
        # This applies if the document has a user field
        return hasattr(obj, 'user') and obj.user == request.user


class IsConversationParticipant(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation to access it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Check if the user is a participant in this conversation
        return obj.user == request.user