import { Concise, Query, Summary } from ".";
import { profile_icon } from "../../../../assets/icons/svg";
import { PrivateContainer } from "../../../../components/Containers";
import { TabNav } from "../../../../components/molecules";
import { PrivateAppbar } from "../../../../layout";
import useInterview from "./useInterview";

export default function SelectedInterview() {
  const {
    summary,
    interviewTranscript,
    concise,
    setActiveTab,
    interviewTitle,
    projectTitle,
    projectId,
  } = useInterview();
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
        />
      }
    >
      <TabNav
        tabs={[
          {
            name: "Summary",
            component: (
              <Summary
                data={summary}
                interviewTranscript={interviewTranscript}
              />
            ),
          },
          {
            name: "Concise",
            component: (
              <Concise
                data={concise}
                interviewTranscript={interviewTranscript}
              />
            ),
          },
          {
            name: "Query",
            component: (
              <Query interviewTranscript={interviewTranscript} />
            ),
          },
        ]}
        activeTabIndex={0}
        onTabChange={(index) => setActiveTab(index)}
      />
    </PrivateContainer>
  );
}
