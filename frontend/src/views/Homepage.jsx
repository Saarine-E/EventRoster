import useCachedFetch from "../hooks/useCachedFetch";
import { Card } from 'primereact/card';
import { ScrollPanel } from 'primereact/scrollpanel'
import { DataTable } from 'primereact/datatable'
import { Column } from 'primereact/column';

export default function Homepage(){

    const { data, loading, error } = useCachedFetch("http://127.0.0.1:8000/events", 60000);

    var events = data;
    console.log(events);
    
    var styles = {display: "grid",
    gridTemplateColumns: "repeat(4, 1fr)",
    gap: "10px",
    padding: "20px"}

    if (loading) return <p>Loading...</p>;
    if (error) return <p>Error: {error.message}</p>;

    return(
        <div style={styles}>
            {events.map((event, index) => {
                return (
                    <Card key={event.eventId} title={event.title} subTitle={event.eventDatetime}>
                        <ScrollPanel style={{ height: '150px' }}>
                            <p>{event.description}</p>
                        </ScrollPanel>
                        <DataTable value={event.groups}>
                            <Column field="name" header="Group"></Column>
                            <Column field="maxMembers" header="Size"></Column>
                        </DataTable>
                    </Card>
                );
            })}
        </div>
    )
}