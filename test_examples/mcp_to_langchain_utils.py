from langchain_core.messages import ToolMessage, HumanMessage
from mcp.types import ImageContent, EmbeddedResource
from pydantic.networks import AnyUrl

def convert_mcp_artifact_types_to_langchain(tool_message: ToolMessage):
    '''
    Convert MCP artifact types to LangChain artifact types.
    '''
    if tool_message.artifact:
        artifacts = tool_message.artifact
        for i, artifact in enumerate(artifacts):
            if isinstance(artifact, ImageContent):
                artifact_content = {
                    "type": "image_url",
                    "image_url": {"url": artifact.data},
                }
                tool_message.artifact[i] = artifact_content
            elif isinstance(artifact, EmbeddedResource):
                if hasattr(artifact, 'resource'):
                    artifact_resource = artifact.resource
                    if hasattr(artifact_resource, 'blob'):
                        artifact_name = artifact_resource.blob
                    else:
                        raise Exception("No blob found in the artifact")
                    if hasattr(artifact_resource, 'uri'):
                        artifact_uri = artifact_resource.uri
                        if isinstance(artifact_uri, AnyUrl):
                            if artifact_uri.scheme:
                                file_data = artifact_uri.scheme + ":" + artifact_uri.path
                            else:
                                file_data = artifact_uri.path
                        else:
                            raise Exception("No uri found in the artifact")
                    else:
                        raise Exception("No uri found in the artifact")
                    artifact_content = {
                        "type": "file",
                        "file": {"filename": artifact_name, "file_data": file_data},
                    }
                else:
                    raise Exception("No resource found in the artifact")
                tool_message.artifact[i] = artifact_content
            else:
                raise NotImplementedError("Artifact type not supported")

    return tool_message

def convert_artifacts_to_human_message(tool_message: ToolMessage):
    '''
    OpenAI API doesn't accept tool messages with files / images in the content, so we need to convert the artifact to a human message.
    '''
    content = [{"type": "text", "text": f'Here are the files returned by the "{tool_message.name}" function.'}]
    if not tool_message.artifact:
        raise Exception("No artifact found in the tool message")
    for artifact in tool_message.artifact:
        content.append(artifact)
    return HumanMessage(content=content)