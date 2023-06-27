import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { axiosInstance } from "./api";
import { projectEndpoints } from "./apiEndpoints";
import { useNavigate } from "react-router-dom";
import { PROJECTS } from "../router/routes.constant";

interface ProjectType {
  id: number;
  goal: string;
  questions: string[];
  title: string;
  start_time: string | null;
  end_time: string | null;
  transcript_count: string | null;
}

interface ProjectPayloadType {
  title?: string;
  goal?: string;
  questions?: string[];
}

const getProjects = async () => {
  const res = await axiosInstance.get(`${projectEndpoints.projectList}`);
  const transformedData = res.data.map((project: ProjectType) => {
    const { start_time, end_time, transcript_count } = project;
    const startTime = start_time
      ? new Date(start_time).toLocaleDateString([], {
          month: "short",
          day: "numeric",
        })
      : "";

    const endTime = end_time
      ? new Date(end_time).toLocaleDateString([], {
          month: "short",
          day: "numeric",
        })
      : "";

    const formattedDate = startTime ? `${startTime} to ${endTime}` : "";
    return {
      id: project.id,
      name: project.title,
      date: formattedDate,
      interviews: transcript_count ? transcript_count : "-",
    };
  });
  return transformedData;
};

const getProject = async (projectId: number | undefined) => {
  const res = await axiosInstance.get(
    `${projectEndpoints.projectList}${projectId}/`
  );

  const transformedData = {
    id: res.data.id,
    name: res.data.title,
    goal: res.data.goal,
    questions: res.data.questions,
  };
  return transformedData;
};

const createProject = async (payload: ProjectPayloadType) => {
  return await axiosInstance.post(`${projectEndpoints.projectList}`, payload);
};

const updateProject = async (
  payload: ProjectPayloadType,
  projectId: number
) => {
  return await axiosInstance.patch(
    `${projectEndpoints.projectList}${projectId}/`,
    payload
  );
};

const deleteProject = async (projectId: number) => {
  return await axiosInstance.delete(
    `${projectEndpoints.projectList}${projectId}/`
  );
};
const useGetProjectsQuery = () => {
  return useQuery(["projects"], getProjects, {
    staleTime: 1000 * 60 * 30, // 30 minutes
  });
};

const useGetProjectMutation = () => {
  return useMutation((projectId: number) => getProject(projectId), {
    onSuccess: (data) => {
      return data;
    },
  });
};
const useGetProjectQuery = (project_id: number | undefined) => {
  return useQuery(["project", project_id], () => getProject(project_id), {
    enabled: !!project_id,
    staleTime: 1000 * 60 * 30, // 30 minutes
  });
};

const useCreateProjectMutation = () => {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  return useMutation((payload: ProjectPayloadType) => createProject(payload), {
    onSuccess: () => {
      queryClient.invalidateQueries(["projects"]);
      setTimeout(() => {
        navigate(PROJECTS.default);
      }, 500);
    },
  });
};

const useDeleteProjectMutation = () => {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  return useMutation((projectId: number) => deleteProject(projectId), {
    onSuccess: () => {
      queryClient.invalidateQueries(["projects"]);
      setTimeout(() => {
        navigate(PROJECTS.default);
      }, 500);
    },
  });
};

const useUpdateProjectMutation = () => {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  return useMutation(
    ({
      payload,
      projectId,
    }: {
      payload: ProjectPayloadType;
      projectId: number;
    }) => updateProject(payload, projectId),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(["projects"]);
        setTimeout(() => {
          navigate(PROJECTS.default);
        }, 500);
      },
    }
  );
};

export {
  updateProject,
  useGetProjectsQuery,
  useGetProjectMutation,
  useGetProjectQuery,
  useCreateProjectMutation,
  useUpdateProjectMutation,
  useDeleteProjectMutation,
};
