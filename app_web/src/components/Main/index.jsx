import { useState, useEffect } from 'react';
import CardUser from '../CardUser';


export default function Main() {

    const [students, setStudents] = useState([{}]);

    useEffect(() => {

        fetch("http://localhost:3000/")
        .then(response => response.json())
        .then(data => {

            setStudents(data);

        });
        
    }, []);

    return (
        <main>

            {students.map(student =>
                <CardUser avatar={student.avatar} name={student.name} turma={student.turma} status={student.status}/>
            )}

        </main>
    );
    
}