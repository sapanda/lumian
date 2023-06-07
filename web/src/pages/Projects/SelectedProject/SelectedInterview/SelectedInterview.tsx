import { Concise, Query, Summary } from ".";
import { updateMeetingTranscript } from "../../../../api/meetingApi";
import { profile_icon } from "../../../../assets/icons/svg";
import { PrivateContainer } from "../../../../components/Containers";
import { TabNav } from "../../../../components/molecules";
import { PrivateAppbar } from "../../../../layout";
import useInterview from "./useInterview";

export default function SelectedInterview() {
  const {
    summary,
    concise,
    interviewTitle,
    projectTitle,
    projectId,
    interviewId,
    refreshInterviewList,
    refreshInterviewData,
  } = useInterview();

  async function onEditEnd(newTitle: string) {
    const res = await updateMeetingTranscript(
      {
        project: parseInt(projectId || "0"),
        title: newTitle,
      },
      parseInt(interviewId || "0")
    );

    if (res?.status === 200) {
      await refreshInterviewData();
      await refreshInterviewList();
    }
  }
  return (
    <PrivateContainer
      appBar={
        <PrivateAppbar
          title={interviewTitle}
          icon={profile_icon}
          breadcrumb={{
            title: projectTitle,
            path: `/project/${projectId}`,
          }}
          isTitleEditable
          onEditEnd={(newTitle) => {
            onEditEnd(newTitle);
          }}
        />
      }
    >
      <TabNav
        tabs={[
          {
            name: "Summary",
            component: <Summary data={summary} />,
          },
          {
            name: "Concise",
            component: <Concise data={concise} />,
          },
          {
            name: "Query",
            component: <Query />,
          },
        ]}
        activeTabIndex={0}
      />
    </PrivateContainer>
  );
}
