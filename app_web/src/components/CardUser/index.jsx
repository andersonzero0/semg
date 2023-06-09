import { useState } from 'react'
import { Circle } from 'lucide-react'
import './style.css'

export default function CardUser(props) {

    let style = {
        background: props.status,
        borderRadius: "50%",
        color: "white"
    }


    return (
        <div className='box_user'>

            <div>
                <img className='avatar' src={props.avatar}/>
            </div>

            <div className='box_infos'>

                <strong><span className='title'>Nome:</span>{props.name}</strong>
                <small>Turma: {props.turma}</small>
                
            </div>

            <div className='box_status'>

                <p>Status:</p>

                <Circle style={style}/>
                
            </div>

        </div>
    )
    
}