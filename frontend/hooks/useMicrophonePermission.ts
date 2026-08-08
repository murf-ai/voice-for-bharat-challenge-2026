import { useEffect, useState } from 'react';

export type MicrophonePermissionStatus = 'granted' | 'denied' | 'prompt' | null;

/**
 * Hook to handle microphone permission checks and errors
 * Returns the current permission status
 */
export function useMicrophonePermission() {
  const [permissionStatus, setPermissionStatus] = useState<MicrophonePermissionStatus>(null);
  const [hasRequestedPermission, setHasRequestedPermission] = useState(false);

  useEffect(() => {
    // Check if permissions API is available
    if (navigator.permissions) {
      navigator.permissions
        .query({ name: 'microphone' as PermissionName })
        .then((result) => {
          setPermissionStatus(result.state as MicrophonePermissionStatus);

          // Listen for permission changes
          result.onchange = () => {
            setPermissionStatus(result.state as MicrophonePermissionStatus);
          };
        })
        .catch(() => {
          // If permissions API fails, try to access media directly
          checkMicrophoneAccess();
        });
    } else {
      // Fallback for browsers without Permissions API
      checkMicrophoneAccess();
    }
  }, []);

  const checkMicrophoneAccess = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      setPermissionStatus('granted');
      // Stop the stream immediately as we're just checking permission
      stream.getTracks().forEach((track) => track.stop());
    } catch (error) {
      if (error instanceof DOMException) {
        if (error.name === 'NotAllowedError') {
          setPermissionStatus('denied');
        } else if (error.name === 'NotFoundError') {
          setPermissionStatus('prompt');
        }
      }
    }
  };

  const requestMicrophoneAccess = async () => {
    setHasRequestedPermission(true);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      setPermissionStatus('granted');
      // Stop the stream as we've confirmed permission
      stream.getTracks().forEach((track) => track.stop());
      return true;
    } catch (error) {
      if (error instanceof DOMException && error.name === 'NotAllowedError') {
        setPermissionStatus('denied');
      }
      return false;
    }
  };

  return {
    permissionStatus,
    hasRequestedPermission,
    requestMicrophoneAccess,
    isDenied: permissionStatus === 'denied',
    isGranted: permissionStatus === 'granted',
  };
}
