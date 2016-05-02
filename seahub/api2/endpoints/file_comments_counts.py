import logging

from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from seaserv import seafile_api
from pysearpc import SearpcError

from seahub.api2.authentication import TokenAuthentication
from seahub.api2.permissions import IsRepoAccessible
from seahub.api2.throttling import UserRateThrottle
from seahub.api2.utils import api_error
from seahub.base.models import FileComment

logger = logging.getLogger(__name__)


class FileCommentsCounts(APIView):
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated, IsRepoAccessible)
    throttle_classes = (UserRateThrottle, )

    def get(self, request, repo_id, format=None):
        """Count all comments of all file under certain parent dir.
        """
        path = request.GET.get('p', '/')
        if not path:
            return api_error(status.HTTP_400_BAD_REQUEST, 'Wrong path.')

        try:
            obj_id = seafile_api.get_dir_id_by_path(repo_id,
                                                    path)
        except SearpcError as e:
            logger.error(e)
            return api_error(status.HTTP_500_INTERNAL_SERVER_ERROR,
                             'Internal error.')
        if not obj_id:
            return api_error(status.HTTP_404_NOT_FOUND, 'Parent dir not found.')

        d = {}
        for o in FileComment.objects.get_by_parent_path(repo_id, path):
            d[o.item_name] = d.get(o.item_name, 0) + 1

        ret = []
        for k, v in d.iteritems():
            ret.append({k: v})

        return Response(ret)
