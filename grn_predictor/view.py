import os

import yaml
from django.http import FileResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers

from betse_app.grn_predictor.s import GRNConfigSerializer


class S(serializers.Serializer):
    gene_functionalities=serializers.ListSerializer(
        child=serializers.CharField(),
        help_text="Cellular Components you want to add (AI Based - Describe or direct call them)"
    )

class CreatGrnView(APIView):
    serializer_class = GRNConfigSerializer

    def hold_content(self, validated_data, user_id):
        new_folder_path = "betse_data"
        os.makedirs(new_folder_path, exist_ok=True)

        file_path=os.path.join(new_folder_path, f"grn_conf_{user_id}.yaml")
        yaml_content = yaml.dump(validated_data, default_flow_style=False, sort_keys=False)
        with open(file_path, "w") as f:
            f.write(yaml_content)
        return file_path

    def post(self, request, *args, **kwargs):
        user_id = "TEST_USER_ID"

        # validate
        serializer = GRNConfigSerializer(data=request.data)  # Use the serializer
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        validated_data = serializer.validated_data  # Get the validated data

        # convert file content & clean up
        file_path = self.hold_content(validated_data, user_id)

        # return
        f = open(file_path, 'rb')
        response = FileResponse(f, as_attachment=True, filename=f"grn_conf_{user_id}.yaml")

        # set callback to remove the file AFTER the response is finished
        response.close = lambda *args, **kwargs: (f.close(), os.remove(file_path))

        return response

        """gene_functionalities = request.data.get("gene_functionalities")
        self.grn_creator = GRNCreator(
            GraphUtils(),
            gene_functionalities=gene_functionalities
        )
        try:
            self.grn_creator.create()

            return JsonResponse({"status": "success"})

        except Exception as e:
            return JsonResponse({"status": f"An error occurred: {e}"})"""

