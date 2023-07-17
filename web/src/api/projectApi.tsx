import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { axiosInstance } from "./api";
import { projectEndpoints } from "./apiEndpoints";
import { useNavigate } from "react-router-dom";
import { PROJECTS } from "../router/routes.constant";
import { AxiosError } from "axios";

interface ProjectType {
  id: number;
  goal: string;
  questions: string[];
  title: string;
  start_time_min: string | null;
  end_time_max: string | null;
  transcript_count: string | null;
}

interface ProjectPayloadType {
  title?: string;
  goal?: string;
  questions?: string[];
}

const getProjects = async () => {
  const res = await axiosInstance.get(`${projectEndpoints.projectList}`);

  if (!res.data.data) return [];
  const transformedData = res.data.data.map((project: ProjectType) => {
    const { start_time_min, end_time_max, transcript_count } = project;
    const startTime = start_time_min
      ? new Date(start_time_min).toLocaleDateString([], {
          month: "short",
          day: "numeric",
        })
      : "";

    const endTime = end_time_max
      ? new Date(end_time_max).toLocaleDateString([], {
          month: "short",
          day: "numeric",
        })
      : "";

    const formattedDate = startTime ? `${startTime} to ${endTime}` : "-";
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
    `${projectEndpoints.projectList}${projectId}/`,
    {
      headers: {
        showToastDisabled: false,
      },
    }
  );

  return res;
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
  const navigate = useNavigate();
  const res = useQuery(["projects"], getProjects, {
    staleTime: 1000 * 60 * 30, // 30 minutes
    retry: false,
    onSuccess: (data) => {
      if (!data.length) {
        navigate(PROJECTS.CREATE_PROJECT);
      } else {
        localStorage.setItem("visited", "true");
      }
    },
  });

  return res;
};

const useGetProjectMutation = () => {
  return useMutation((projectId: number) => getProject(projectId), {
    onSuccess: (data) => {
      return data;
    },
  });
};
const useGetProjectQuery = (project_id: number | undefined) => {
  const res = useQuery(["project", project_id], () => getProject(project_id), {
    enabled: !!project_id,
    staleTime: 1000 * 60 * 30, // 30 minutes
    retry: false,
    select: (res) => {
      const transformedData = {
        id: res.data.data.id,
        name: res.data.data.title,
        goal: res.data.data.goal,
        questions: res.data.data.questions,
      };
      return transformedData;
    },
    onError: (err: AxiosError) => {
      if (err.response?.status === 404) {
        navigate("/404");
      }
    },
  });
  const navigate = useNavigate();

  return res;
};

const useCreateProjectMutation = () => {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  return useMutation((payload: ProjectPayloadType) => createProject(payload), {
    onSuccess: (data) => {
      const id = data.data.data.id;

      queryClient.invalidateQueries(["projects"]);
      setTimeout(() => {
        navigate(PROJECTS.SELECTED_PROJECT.default.replace(":projectId", id));
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
      onSuccess: (_, variables) => {
        const { projectId } = variables;
        queryClient.invalidateQueries(["projects"]);

        setTimeout(() => {
          navigate(
            PROJECTS.SELECTED_PROJECT.default.replace(
              ":projectId",
              `${projectId}`
            )
          );
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
